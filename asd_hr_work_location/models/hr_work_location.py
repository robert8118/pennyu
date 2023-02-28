from odoo import models, fields, api

class HrWorkLocation(models.Model):
    _name = 'hr.work.location'
    _description = 'Hr Work Location'
    
    name = fields.Char('Name')
    company_code = fields.Char('Company Code')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            if rec.company_code:
                res.append((rec.id, '%s - %s' % (rec.company_code, rec.name)))
            else:
                res.append((rec.id, '%s' % (rec.name)))
        return res