from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Beberapa cara track setiap perubahan pada record Contact dan Employee:
    # 1. Override beberapa field yang ada di modul Contact dan Employee dengan penambahan atribut field track_visibility
    # 2. Tambah field baru yang relasi ke write_uid dan write_date

    name = fields.Char(track_visibility='onchange')
    # Work Information
    ## Contact Information
    address_id = fields.Many2one(track_visibility='onchange')
    work_email = fields.Char(track_visibility='onchange')
    mobile_phone = fields.Char(track_visibility='onchange')
    work_phone = fields.Char(track_visibility='onchange')
    ## Position
    department_id = fields.Many2one(track_visibility='onchange')
    job_id = fields.Many2one(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    coach_id = fields.Many2one(track_visibility='onchange')
    manager = fields.Boolean(track_visibility='onchange')
    resource_calendar_id = fields.Many2one(track_visibility='onchange')

    # Private Information
    ## Citizenship & Other Information
    country_id = fields.Many2one(track_visibility='onchange')
    identification_id = fields.Char(track_visibility='onchange')
    passport_id = fields.Char(track_visibility='onchange')
    bank_account_id = fields.Many2one(track_visibility='onchange')
    ## Status
    gender = fields.Selection(track_visibility='onchange')
    marital = fields.Selection(track_visibility='onchange')
    children = fields.Integer(track_visibility='onchange')
    ## Work Permit
    permit_no = fields.Char(track_visibility='onchange')
    visa_no = fields.Char(track_visibility='onchange')
    visa_expire = fields.Date(track_visibility='onchange')
    ## Contact Information
    address_home_id = fields.Many2one(track_visibility='onchange')
    ## Birth
    birthday = fields.Date(track_visibility='onchange')
    place_of_birth = fields.Char(track_visibility='onchange')

    # HR Settings
    ## Status
    company_id = fields.Many2one(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    ## Current Contract
    medic_exam = fields.Date(track_visibility='onchange')
    vehicle = fields.Char(track_visibility='onchange')
    vehicle_distance = fields.Integer(track_visibility='onchange')
    
    