from odoo import api, fields, models, _


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)
        if res.get('product_return_moves'):
            for i in range(0, len(res['product_return_moves'])):
                res['product_return_moves'][i][2]['to_refund'] = True
        return res
