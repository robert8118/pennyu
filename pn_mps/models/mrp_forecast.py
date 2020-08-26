from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import expression


class SaleForecastExtend(models.Model):
    _inherit = 'sale.forecast'

    @api.model
    def _prepare_procurement(self, product, date):
        """
        Set manufacture_to_resupply = True only to warehouse that used to produce/manufacture
        """
        location_ids = [{x: [i.location_id.id for i in x.pull_ids if i.action == 'manufacture']} for x in
                        product.route_ids]
        location_ids = [{k: v for k, v in x.items() if v != []} for x in location_ids]
        location_ids = [x for x in location_ids if x != {}]
        if location_ids:
            location_ids = [v for v in location_ids[0].values()]
            location_ids = location_ids[0]
        else:
            location_ids = [{x: [i.location_id.id for i in x.pull_ids if i.action == 'manufacture']} for x in
                            product.categ_id.total_route_ids]
            location_ids = [{k: v for k, v in x.items() if v != []} for x in location_ids]
            location_ids = [x for x in location_ids if x != {}]
            if location_ids:
                location_ids = [v for v in location_ids[0].values()]
                location_ids = location_ids[0]

        warehouses = self.env['stock.warehouse'].search([('manufacture_to_resupply', '=', True)])
        if location_ids:
            warehouses = warehouses.filtered(lambda x: x.manu_type_id.default_location_src_id.id in location_ids)
        return {
            'date_planned': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'company_id': self.env.user.company_id,
            'warehouse_id': warehouses[0] if warehouses else False,
            'add_date_in_domain': True,
        }

    @api.model
    def _action_procurement_create(self, product, to_supply, date):
        if to_supply:
            vals = self._prepare_procurement(product, date)
            warehouse = vals['warehouse_id']
            location = warehouse.lot_stock_id if warehouse else False
            self.env['procurement.group'].run(product, to_supply, product.uom_id, location, product.name, 'MPS', vals)
        return False


class ProcurementGroupExtend(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _search_rule(self, product_id, values, domain):
        """ Add priority route in product. route product first, then route product category """
        if values.get('warehouse_id', False):
            domain = expression.AND(
                [['|', ('warehouse_id', '=', values['warehouse_id'].id), ('warehouse_id', '=', False)], domain])
        Pull = self.env['procurement.rule']
        res = self.env['procurement.rule']
        if values.get('route_ids', False):
            res = Pull.search(expression.AND([[('route_id', 'in', values['route_ids'].ids)], domain]),
                              order='route_sequence, sequence', limit=1)
        if not res:
            product_routes = product_id.route_ids
            if not product_routes:
                product_routes = product_id.categ_id.total_route_ids
            if product_routes:
                res = Pull.search(expression.AND([[('route_id', 'in', product_routes.ids)], domain]),
                                  order='route_sequence, sequence', limit=1)
        if not res:
            warehouse_routes = values['warehouse_id'].route_ids
            if warehouse_routes:
                res = Pull.search(expression.AND([[('route_id', 'in', warehouse_routes.ids)], domain]),
                                  order='route_sequence, sequence', limit=1)
        return res
