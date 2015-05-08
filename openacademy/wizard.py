# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Wizard(models.TransientModel):
    _name = 'openacademy.wizard'

    def _default_sessions(self):
        return self.env['openacademy.session'].browse(self._context.get('active_ids'))

    state = fields.Char(selection=(('draft','draft'),('select','select')), default='draft')
    session_ids = fields.Many2many('openacademy.session',
        string="Session", required=True, default=_default_sessions)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    
    @api.one
    def add_attendees(self):
        for session in self.session_ids:
            session.attendee_ids |= self.attendee_ids
        
    @api.multi
    def go_select(self):
        self.write({'state': 'select'})
        return {
            'name': 'Select attendees',
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'openacademy.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self[0].id,
        }
    
    @api.multi
    def go_draft(self):
        self.write({'state': 'draft'})
        return {
            'name': 'Select session',
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'openacademy.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self[0].id,
        }
        
    @api.multi
    def report(self):
        res = self.env['report'].get_action(self, 'openacademy.report_wizard_view')
        return res