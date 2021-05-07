from odoo import api, fields, models
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        non_avaiable_product = []
        for line in self.order_line:
            if line.product_id.qty_available <= 0 and line.product_id.virtual_available <= 0:
                non_avaiable_product.append(line.product_id.name)
        if non_avaiable_product:
            non_avaiable_product = ', '.join(non_avaiable_product)
            raise Warning('Product(s): %s has zero on hand quantity or lower and so its forecasted quantity' % (
                non_avaiable_product))

        res = super(SaleOrder, self).action_confirm()
        return res
