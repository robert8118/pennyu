from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    qty_target = fields.Float('Qty Target')
    uom_qty_target = fields.Many2one('product.uom', 'UoM')
    spv_id = fields.Many2one('res.users', 'Supervisor')

    @api.model
    def create(self, vals):
        vals['qty_target'] = vals.get('product_qty')
        vals['uom_qty_target'] = vals.get('product_uom_id')
        res = super(MrpProduction, self).create(vals)
        return res
