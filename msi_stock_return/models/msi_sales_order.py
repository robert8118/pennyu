# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018 Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round



class Picking_msi(models.Model):
    _inherit = "stock.picking"

    move_return_id = fields.One2many('msi_stock_return', 'move_return_ids', string="Stock Moves Return", copy=True)


class Msi_Stock_Return(models.Model):
    _name = "msi_stock_return"
    _description = "Stock Move Return"

    product_id = fields.Many2one('product.product', 'Product',index=True, required=True,)
    qty = fields.Float('Return Quantity', digits=dp.get_precision('Product Unit of Measure'))
    move_return_ids = fields.Many2one('stock.picking', 'Picking')

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    _description = 'Return Picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = {
            'product_id': return_line.product_id.id,
            'product_uom_qty': return_line.quantity,
            'product_uom': return_line.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'location_id': return_line.move_id.location_dest_id.id,
            'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line.move_id.id,
            'procure_method': 'make_to_stock',
        }
        return vals
    
    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError("You may only return one picking at a time!")
        res = super(StockReturnPicking, self).default_get(fields)
        #print ('---res--',res)
        move_dest_exists = False
        product_return_moves = []
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        quantity_r = 0
        if picking:
            res.update({'picking_id': picking.id})
            if picking.state != 'done':
                raise UserError(_("You may only return Done pickings"))
            for move in picking.move_lines:
                if move.scrapped:
                    continue
                if move.move_dest_ids:
                    move_dest_exists = True


                self.env.cr.execute('SELECT sum(qty) FROM public.msi_stock_return WHERE move_return_ids = %s AND product_id = %s ' ,(picking.id, move.product_id.id))
                hasil = self.env.cr.fetchall()
                if hasil:
                    for row in hasil: 
                    #raise UserError(row[0])
                        result = row[0]
                        if result is None:
                            quantity_r = 0
                        else:
                            quantity_r = float(row[0])

                 
                quantity = move.product_qty - quantity_r
#                quantity = float_round(quantity, precision_rounding=move.product_uom.rounding)
                product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'quantity_done': quantity, 'quantity_new': quantity, 'move_id': move.id, 'uom_id': move.product_id.uom_id.id}))

            if not product_return_moves:
                raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': product_return_moves})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': move_dest_exists})
            if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
                res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
            if 'original_location_id' in fields:
                res.update({'original_location_id': picking.location_id.id})
            if 'location_id' in fields:
                location_id = picking.location_id.id
                if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                    location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
                res['location_id'] = location_id
        return res

#     def _create_returns(self):
#         picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
#         return_obj = self.env['msi_stock_return']
#  
#         # TODO sle: the unreserve of the next moves could be less brutal
#         for return_move in self.product_return_moves.mapped('move_id'):
#             return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()
#  
#         # create new picking for returned products
#         picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
#         new_picking = self.picking_id.copy({
#             'move_lines': [],
#             'picking_type_id': picking_type_id,
#             'state': 'draft',
#             'origin': _("Return of %s") % self.picking_id.name,
#             'location_id': self.picking_id.location_dest_id.id,
#             'location_dest_id': self.location_id.id})
#         new_picking.message_post_with_view('mail.message_origin_link',
#             values={'self': new_picking, 'origin': self.picking_id},
#             subtype_id=self.env.ref('mail.mt_note').id)
#         returned_lines = 0
#         for return_line in self.product_return_moves:
#             if not return_line.move_id:
#                 raise UserError(_("You have manually created product lines, please delete them to proceed"))
#             # TODO sle: float_is_zero?
#             if return_line.quantity:
#                 if return_line.quantity >  return_line.quantity_done:
#                     raise UserError(_("Quantity Return cannot bigger than Qauntity Delivered\n CLOSE RETURN AND START AGAIN"))
#  
#                 return_obj.create({
#                     'move_return_ids': picking.id,
#                     'product_id': return_line.product_id.id,
#                     'qty': return_line.quantity,
#  
#                 })
#  
#                 returned_lines += 1
#                 vals = self._prepare_move_default_values(return_line, new_picking)
#                 r = return_line.move_id.copy(vals)
#                 vals = {}
#  
#                 # +--------------------------------------------------------------------------------------------------------+
#                 # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
#                 # |              | returned_move_ids              ↑                                  | returned_move_ids
#                 # |              ↓                                | return_line.move_id              ↓
#                 # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
#                 # +--------------------------------------------------------------------------------------------------------+
#                 move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
#                 move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
#                 vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]
#                 vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
#                 r.write(vals)
#  
#         if not returned_lines:
#             raise UserError(_("Please specify at least one non-zero quantity."))
#  
#         new_picking.action_confirm()
#         new_picking.action_assign()
#         return new_picking.id, picking_type_id
    
    
    
#     @api.multi
#     def _create_returns(self):
#         # Prevent copy of the carrier and carrier price when generating return picking
#         # (we have no integration of returns for now)
#         new_picking, pick_type_id = super(StockReturnPicking, self)._create_returns()
#         picking = self.env['stock.picking'].browse(new_picking)
#         picking.write({'carrier_id': False,
#                        'carrier_price': 0.0})
#         return new_picking, pick_type_id
    
    
    @api.multi
    def _create_returns(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        new_picking_id, pick_type_id = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse([new_picking_id])
        for move in new_picking.move_lines:
            return_picking_line = self.product_return_moves.filtered(lambda r: r.move_id == move.origin_returned_move_id)
            if return_picking_line and return_picking_line.to_refund:
                move.to_refund = True
            self.env['msi_stock_return'].create({
               'move_return_ids': picking.id,
               'product_id': return_picking_line.product_id.id,
               'qty': return_picking_line.quantity,
            })
        return new_picking_id, pick_type_id


class ReturnPickingLine_msi(models.TransientModel):
    _inherit = "stock.return.picking.line"

    quantity_done = fields.Float("Quantity", digits=dp.get_precision('Product Unit of Measure'))
    quantity_new = fields.Float("Quantity Return", digits=dp.get_precision('Product Unit of Measure'))















