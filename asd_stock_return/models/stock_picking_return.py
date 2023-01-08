from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError("You may only return one picking at a time!")
        res = super(StockReturnPicking, self).default_get(fields)
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

                # Search product_qty pada stock_move yang berstatus cancel
                cancel_qty = self.env['stock.move'].search([('origin_returned_move_id', '=', move.id), ('product_id', '=', move.product_id.id), ('state', '=', 'cancel'), ('is_done', '=', True)]).mapped('product_qty')
                if cancel_qty:
                    quantity = move.product_qty - quantity_r + sum(cancel_qty)
                else:
                    quantity = move.product_qty - quantity_r

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
