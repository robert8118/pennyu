from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class SaleForecastExtend(models.Model):
    _inherit = 'sale.forecast'

    @api.model
    def _prepare_procurement(self, product, date):
        """
        Set manufacture_to_resupply = True only to warehouse that used to produce/manufacture
        """
        warehouse = self.env['stock.warehouse'].search([('manufacture_to_resupply', '=', True)])
        warehouse = [([i for i in x.product_categs_to_manufacture if i.id == product.categ_id.id], x) for x in
                     warehouse] if warehouse else False
        return {
            'date_planned': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'company_id': self.env.user.company_id,
            'warehouse_id': warehouse[0][1] if warehouse else False,
            'add_date_in_domain': True,
        }

    @api.model
    def _action_procurement_create(self, product, to_supply, date):
        if to_supply:
            vals = self._prepare_procurement(product, date)
            warehouse = self.env['stock.warehouse'].search([('manufacture_to_resupply', '=', True)])
            warehouse = [([i for i in x.product_categs_to_manufacture if i.id == product.categ_id.id], x) for x in
                         warehouse] if warehouse else False
            location = warehouse[0][1].lot_stock_id if warehouse else False
            self.env['procurement.group'].run(product, to_supply, product.uom_id, location, product.name, 'MPS', vals)
        return False
