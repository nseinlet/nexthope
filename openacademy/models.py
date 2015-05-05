# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError

class Course(models.Model):
    _name = 'openacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users',
        ondelete='set null', string="Responsible", index=True)
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
        