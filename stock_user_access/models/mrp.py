from odoo import models, fields, api


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    wc_user_ids = fields.Many2many('res.users', string='Allowed Users')


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    wo_user_id = fields.Many2one('res.users', compute='compute_wo_user_id', string='Responsible')

    def compute_wo_user_id(self):
        for rec in self:
            rec.wo_user_id = rec.production_id.user_id.id
