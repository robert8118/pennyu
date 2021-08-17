from odoo import api, fields, models
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        non_avaiable_product = []
        for line in self.order_line:
            if line.product_uom_qty > line.product_id.virtual_available:
                non_avaiable_product.append('- %s. Forcasted Qty: %s' % (line.product_id.name, line.product_id.virtual_available))
        if non_avaiable_product:
            non_avaiable_product = '\n'.join(non_avaiable_product)
            raise Warning("These product(s) has order quantity more than forcasted quantity: \n%s" % (
                non_avaiable_product))

        res = super(SaleOrder, self).action_confirm()
        return res
