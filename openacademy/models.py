# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError
from datetime import timedelta

class Course(models.Model):
    _name = 'openacademy.course'
    _inherit = 'mail.thread'
    _description = "Activite"
    
    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users',
        ondelete='set null', string="Responsible", index=True, track_visibility='onchange', copy=False)
    session_ids = fields.One2many('openacademy.session', 'course_id', string='Sessions')
    nbr_session = fields.Integer('Nombre de sessions', compute='_get_nbr_sessions')
    responsible_name = fields.Char(compute='_get_responsible_name')
    name2 = fields.Char(compute='_compute_name')
    value = fields.Integer()
    
    @api.multi
    def _get_nbr_sessions(self):
        for cours in self:
            cours.nbr_session = len(cours.session_ids)
             
    @api.one
    @api.depends('responsible_id')
    def _get_responsible_name(self):
        self.responsible_name = "Le responsable est %s" % self.responsible_id.name
    
    @api.one
    @api.depends('value')
    def _compute_name(self):
        self.name2 = "Record with value %s" % self.value
    
    @api.one
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)
        
    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]
    
class Session(models.Model):
    _name = 'openacademy.session'
    
    def _get_default_color(self):
        return "Bleu"
    
    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    country_id = fields.Many2one('res.country')
    instructor_id = fields.Many2one('res.partner', string="Instructor")
    phone = fields.Char(related='instructor_id.phone')
    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string="Course", required=True)
    sequence = fields.Integer("Sequence")
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    couleur = fields.Char(default=_get_default_color)
    end_date = fields.Date(string="End Date", store=True,
        compute='_get_end_date', inverse='_set_end_date')
    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')
    nbr_attendees = fields.Integer(compute='_get_nbr_attendees', store=True)
    
    @api.one
    @api.depends('attendee_ids')
    def _get_nbr_attendees(self):
        self.nbr_attendees = len(self.attendee_ids)
        
    @api.one
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        if not self.seats:
            self.taken_seats = 0.0
        else:
            self.taken_seats = 100.0 * len(self.attendee_ids) / self.seats
            
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }
            
    @api.one
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        if self.instructor_id and self.instructor_id in self.attendee_ids:
            raise ValidationError("A session's instructor can't be an attendee")
    
    @api.one
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        if not (self.start_date and self.duration):
            self.end_date = self.start_date
            return

        # Add duration to start_date, but: Monday + 5 days = Saturday, so
        # subtract one second to get on Friday instead
        start = fields.Datetime.from_string(self.start_date)
        duration = timedelta(days=self.duration, seconds=-1)
        self.end_date = start + duration
        
    @api.one
    def _set_end_date(self):
        if not (self.start_date and self.end_date):
            return

        # Compute the difference between dates, but: Friday - Monday = 4 days,
        # so add one day to get 5 days instead
        start_date = fields.Datetime.from_string(self.start_date)
        end_date = fields.Datetime.from_string(self.end_date)
        self.duration = (end_date - start_date).days + 1
    
    @api.one
    @api.depends('duration')
    def _get_hours(self):
        self.hours = self.duration * 24

    @api.one
    def _set_hours(self):
        self.duration = self.hours / 24
                