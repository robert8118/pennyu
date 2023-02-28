from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # work_location_id = fields.Many2one('hr.work.location', string='Work Location')
    work_location_id = fields.Many2one('hr.work.location', string='Work Location', track_visibility='onchange')
    