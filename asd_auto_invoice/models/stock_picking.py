from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_return_type(self, pick_type_code, is_return):
        return_type = False
        if is_return:
            if pick_type_code == 'incoming':
                return_type = 'incoming'
            elif pick_type_code == 'outgoing':
                return_type = 'outgoing'
        return return_type
    
    def _get_order_type(self, picking_id, is_return):
        pick_type_temp, order_type = False, False
        
        # incoming_return: do_return, return_of_gr_return
        # outgoing_return: gr_return, return_of_do_return
        if not is_return:
            if picking_id.picking_type_id.code == 'incoming':
                pick_type_temp = 'incoming'
            elif picking_id.picking_type_id.code == 'outgoing':
                pick_type_temp = 'outgoing'
        else:
            if picking_id.picking_type_id.code == 'incoming':
                pick_type_temp = 'incoming_return'
            elif picking_id.picking_type_id.code == 'outgoing':
                pick_type_temp = 'outgoing_return'
        
        if not picking_id.group_id.sale_id:
            if pick_type_temp in ['incoming', 'incoming_return', 'outgoing_return']:
                order_type = 'purchase'
        else:
            if pick_type_temp in ['outgoing', 'outgoing_return', 'incoming_return']:
                order_type = 'sale'

        return order_type

    def auto_invoice(self, picking_id=None, return_status=False):
        picking_obj = self.env['stock.picking']
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        if self:
            sp_id = self
        else:
            sp_id = picking_id
        if sp_id.group_id:
            data = {}
            
            order_type = self._get_order_type(picking_id=sp_id, is_return=return_status)
            return_type = self._get_return_type(pick_type_code=sp_id.picking_type_id.code, is_return=return_status)

            if return_status:
                data.update({'name': sp_id.origin})
                sp_origin_name = sp_id.origin.replace('Return of', '').strip()
                sp_origin = picking_obj.search([('name', '=', sp_origin_name)], limit=1)
                ai = invoice_obj.search(
                    [('origin', '=', f'{sp_origin.group_id.name}: {sp_origin_name}')], limit=1)
                if ai.state == 'draft':
                    sp_id.decrease_qty_invoice(ai, order_type)
                    return False

            invoice_id = ai if return_status else False
            invoice_data = self._prepare_data_account_invoice(order_type=order_type, return_type=return_type, picking_id=sp_id, invoice_id=invoice_id, data=data)
            # replace data with invoice_data
            data = invoice_data
            
            order_id = data.get('order_id')
            data.update({
                'date_invoice': fields.Date.today(),
                'release_to_pay': 'yes',
                'partner_id': data.get('partner_id') or sp_id.partner_id.id,
            })
            inv = invoice_obj.create(data)
            for move in sp_id.move_lines:
                if move.quantity_done:
                    invoice_data_line = self._prepare_data_account_invoice_line(order_type=order_type, move=move, invoice_id=inv, order_id=order_id)
                    inv_line = invoice_line_obj.create(invoice_data_line)
                    if sp_id.picking_type_id.code == 'outgoing':
                        move.sale_line_id.update({
                            'invoice_lines': [(4, inv_line.id, 0)]
                        })
            inv.compute_taxes()
            return inv
        else:
            return False
        
    def _prepare_data_account_invoice(self, order_type, return_type, picking_id, invoice_id, data={}):
        journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']
        sale_group_id = picking_id.group_id.sale_id

        if order_type == 'purchase':
            if not return_type or return_type == 'incoming':
                invoice_type = 'in_invoice'
            elif return_type == 'outgoing':
                invoice_type = 'in_refund'
            order_obj = self.env['purchase.order']
            internal_type = 'payable'
        elif order_type == 'sale':
            if not return_type or return_type == 'outgoing':
                invoice_type = 'out_invoice'
            elif return_type == 'incoming':
                invoice_type = 'out_refund'
            order_obj = self.env['sale.order']
            internal_type = 'receivable'
        
        order_domain = [('name', '=', picking_id.group_id.name)]
        order_id = order_obj.search(order_domain, limit=1)
        # Handling return of Delivery Order (DO) return
        return_of_do_return = order_type == 'purchase' and not order_id and sale_group_id
        if return_of_do_return:
            order_id = sale_group_id
        if not order_id:
            raise ValidationError(_('order_id not found'))
        
        origin = f'{order_id.name}: {picking_id.name}' if not return_type else invoice_id.number
        payment_term_id = order_id.payment_term_id.id
        company_id = order_id.company_id.id
        user_id = order_id.user_id.id if order_type == 'sale' else self._uid
        
        journal_domain = [
            ('company_id', '=', company_id),
            ('type', '=', order_type)
        ]
        journal_id = journal_obj.search(journal_domain, limit=1)
        
        account_domain = [
            ('internal_type', '=', internal_type),
            ('company_id', '=', company_id),
            ('deprecated', '=', False)
        ]
        account_id = account_obj.search(account_domain, limit=1)
        
        data.update({
            'order_id': order_id,
            'type': invoice_type,
            'origin': origin,
            'payment_term_id': payment_term_id,
            'company_id': company_id,
            'journal_id': journal_id[:1].id,
            'account_id': account_id[:1].id,
            'user_id': user_id,
        })
        
        if order_type == 'purchase':
            if sale_group_id and order_id != sale_group_id:
                data.update({
                        'reference': order_id.partner_ref
                    })
        elif order_type == 'sale':
            data.update({
                'partner_id': order_id.partner_invoice_id.id or order_id.partner_id.id,
                'partner_shipping_id': order_id.partner_shipping_id.id,
                'team_id': order_id.team_id.id
            })
        return data
        
    def _prepare_data_account_invoice_line(self, order_type, move, invoice_id, order_id):
        account_obj = self.env['account.account']
        data_line = {
            'invoice_id': invoice_id.id,
            'product_id': move.product_id.id,
            'quantity': move.quantity_done,
            'uom_id': move.product_uom.id
        }

        if order_type == 'purchase':
            account_code = '202100'
            order_line = move.purchase_line_id
            tax_ids = [(6, 0, order_line.taxes_id.mapped('id'))]
            analytic_account_id = order_line.account_analytic_id.id
            data_line.update({
                'purchase_line_id': order_line.id,
            })
        elif order_type == 'sale':
            account_code = '400100'
            order_line = move.sale_line_id
            tax_ids = [(6, 0, order_line.tax_id.mapped('id'))]
            analytic_account_id = order_id.analytic_account_id.id
            data_line.update({
                'sale_line_id': order_line.id,
                'discount': order_line.discount
            })
        
        product_name = '%s: %s' % (order_id.name, move.product_id.display_name)
        account_domain = [('code', '=', account_code), ('company_id', '=', invoice_id.company_id.id)]
        account_id = account_obj.search(account_domain, limit=1).id

        price_unit = order_line.price_unit / move.product_uom.factor * order_line.product_uom.factor

        data_line.update({
            'name': product_name,
            'account_analytic_id': analytic_account_id,
            'account_id': account_id,
            'price_unit': price_unit,
            'invoice_line_tax_ids': tax_ids,
        })

        return data_line
