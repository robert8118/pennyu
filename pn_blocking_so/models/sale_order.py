from odoo import api, fields, models
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        non_avaiable_product = []
        for line in self.order_line:
            if line.product_uom_qty > line.product_id.virtual_available:
                non_avaiable_product.append(line.product_id.name)
        if non_avaiable_product:
            non_avaiable_product = ', '.join(non_avaiable_product)
            raise Warning("Can't order product(s): %s because below forecasted quantity" % (
                non_avaiable_product))

        res = super(SaleOrder, self).action_confirm()
        return res
