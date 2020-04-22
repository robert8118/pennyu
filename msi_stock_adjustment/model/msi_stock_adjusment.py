import xlsxwriter
import base64
from odoo import fields, models, api
from io import BytesIO
from datetime import datetime
from pytz import timezone
import pytz

from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class MsiProductcategory(models.Model):
    _inherit = "product.category"
    
    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))
    
    property_stock_adjustment_in = fields.Many2one(
        'account.account', 'Stock Adjusment In', company_dependent=True,
        domain=[('deprecated', '=', False)],)


    property_stock_adjustment_out = fields.Many2one(
        'account.account', 'Stock Adjusment Out', company_dependent=True,
        domain=[('deprecated', '=', False)],)


class MsiProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"
    _description = "Change Product Quantity"

    def _action_start_line(self):
        move = self.env['account.move']
        move_line = self.env['account.move.line']
        product = self.product_id.with_context(location=self.location_id.id, lot_id=self.lot_id.id)
        th_qty = product.qty_available
        th_cost = product.standard_price

        jurnal = move.create({

                'ref': 'Stock Adjustment',
                'journal_id': 8,
                'company_id': self.env.user.company_id.id,
#                'name': 'test',
        })
        jurnal_id = jurnal['id']


        if self.new_quantity > th_qty: 

               selisih_qty = self.new_quantity - product.qty_available
               selisih_cost = (self.new_quantity - product.qty_available)*th_cost
   
               data3 = move_line.with_context(check_move_validity=False).create({
                'move_id': jurnal_id,
                'name': 'INV:INV: '+ product.name,
                'company_id': self.env.user.company_id.id,
                'account_id': product.categ_id.property_stock_account_input_categ_id.id,
                'credit': selisih_cost,
                'quantity': selisih_qty,

               })

               data4 = move_line.with_context(check_move_validity=False).create({
                'move_id': jurnal_id,
                'name': 'INV:INV: '+ product.name,
                'company_id': self.env.user.company_id.id,
                'account_id': product.categ_id.property_stock_adjustment_in.id,
                'debit': selisih_cost,
                'quantity': selisih_qty,

               })
               jurnal.post()

        else:

               selisih_qty = (self.new_quantity - product.qty_available)*-1
               selisih_cost = selisih_qty*th_cost

               data3 = move_line.with_context(check_move_validity=False).create({
                'move_id': jurnal_id,
                'name': 'INV:INV: '+ product.name,
                'company_id': self.env.user.company_id.id,
                'account_id': product.categ_id.property_stock_account_output_categ_id.id,
                'credit': selisih_cost,
                'quantity': selisih_qty,

               })

               data4 = move_line.with_context(check_move_validity=False).create({
                'move_id': jurnal_id,
                'name': 'INV:INV: '+ product.name,
                'company_id': self.env.user.company_id.id,
                'account_id': product.categ_id.property_stock_adjustment_out.id,
                'debit': selisih_cost,
                'quantity': selisih_qty,

               })
               jurnal.post()


        res = {
               'product_qty': self.new_quantity,
               'location_id': self.location_id.id,
               'product_id': self.product_id.id,
               'product_uom_id': self.product_id.uom_id.id,
               'theoretical_qty': th_qty,
               'prod_lot_id': self.lot_id.id,
        }

        return res


    def change_product_qty(self):
        """ Changes the Product Quantity by making a Physical Inventory. """
        Inventory = self.env['stock.inventory']


        for wizard in self:
            product = wizard.product_id.with_context(location=wizard.location_id.id, lot_id=wizard.lot_id.id)
            line_data = wizard._action_start_line()


            if wizard.product_id.id and wizard.lot_id.id:
                inventory_filter = 'none'
            elif wizard.product_id.id:
                inventory_filter = 'product'
            else:
                inventory_filter = 'none'
            inventory = Inventory.create({
                'name': _('INV: %s') % tools.ustr(wizard.product_id.display_name),
                'filter': inventory_filter,
                'product_id': wizard.product_id.id,
                'location_id': wizard.location_id.id,
                'lot_id': wizard.lot_id.id,
                'line_ids': [(0, 0, line_data)],
            })
            inventory.action_done()
        return {'type': 'ir.actions.act_window_close'}

