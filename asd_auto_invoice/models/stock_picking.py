from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
            sale_group_id = sp_id.group_id.sale_id
            
            # outgoing_return: gr_return, return_of_do_return
            # incoming_return: do_return, return_of_gr_return
            outgoing_return = sp_id.picking_type_id.code == 'outgoing' and return_status
            incoming_return = sp_id.picking_type_id.code == 'incoming' and return_status
            
            gr_transfer = sp_id.picking_type_id.code == 'incoming' and not return_status
            do_transfer = sp_id.picking_type_id.code == 'outgoing' and not return_status
            
            purchase_status = not sale_group_id and (gr_transfer or outgoing_return or incoming_return)
            sale_status = sale_group_id != False and (do_transfer or incoming_return or outgoing_return)

            if return_status:
                sp_origin_name = sp_id.origin.replace('Return of', '').strip()
                sp_origin = picking_obj.search([('name', '=', sp_origin_name)], limit=1)
                ai = invoice_obj.search(
                    [('origin', '=', f'{sp_origin.group_id.name}: {sp_origin_name}')], limit=1)
                if ai.state == 'draft':
                    pick_from = 'purchase' if purchase_status else 'sale'
                    sp_id.decrease_qty_invoice(ai, pick_from)
                    return False

            if return_status:
                data.update({
                    'name': sp_id.origin
                })
                if outgoing_return:
                    return_type = 'outgoing'
                elif incoming_return:
                    return_type = 'incoming'

            invoice_id = ai if return_status else False
            if purchase_status:
                status_type = 'purchase'
            elif sale_status:
                status_type = 'sale'
            invoice_data = self._prepare_data_account_invoice(status_type=status_type, picking_id=sp_id, invoice_id=invoice_id, return_type=return_type, data=data)
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
                    invoice_data_line = self._prepare_data_account_invoice_line(status_type=status_type, move=move, invoice_id=inv, order_id=order_id)
                    inv_line = invoice_line_obj.create(invoice_data_line)
                    if sp_id.picking_type_id.code == 'outgoing':
                        move.sale_line_id.update({
                            'invoice_lines': [(4, inv_line.id, 0)]
                        })
            inv.compute_taxes()
            return inv
        else:
            return False
        
    def _prepare_data_account_invoice(self, status_type, picking_id, invoice_id, return_type=False, data={}):
        journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']
        sale_group_id = picking_id.group_id.sale_id

        if status_type == 'purchase':
            if not return_type or return_type == 'incoming':
                invoice_type = 'in_invoice'
            elif return_type == 'outgoing':
                invoice_type = 'in_refund'
            order_obj = self.env['purchase.order']
            internal_type = 'payable'
        elif status_type == 'sale':
            if not return_type or return_type == 'outgoing':
                invoice_type = 'out_invoice'
            elif return_type == 'incoming':
                invoice_type = 'out_refund'
            order_obj = self.env['sale.order']
            internal_type = 'receivable'
        
        order_domain = [('name', '=', picking_id.group_id.name)]
        order_id = order_obj.search(order_domain, limit=1)
        # Handling return of Delivery Order (DO) return
        return_of_do_return = status_type == 'purchase' and not order_id and sale_group_id
        if return_of_do_return:
            order_id = sale_group_id
        if not order_id:
            raise ValidationError(_('order_id not found'))
        
        origin = f'{order_id.name}: {picking_id.name}' if not return_type else invoice_id.number
        payment_term_id = order_id.payment_term_id.id
        company_id = order_id.company_id.id
        user_id = order_id.user_id.id if status_type == 'sale' else self._uid
        
        journal_domain = [
            ('company_id', '=', company_id),
            ('type', '=', status_type)
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
        
        if status_type == 'purchase':
            if sale_group_id and order_id != sale_group_id:
                data.update({
                        'reference': order_id.partner_ref
                    })
        elif status_type == 'sale':
            data.update({
                'partner_id': order_id.partner_invoice_id.id or order_id.partner_id.id,
                'partner_shipping_id': order_id.partner_shipping_id.id,
                'team_id': order_id.team_id.id
            })
        return data
        
    def _prepare_data_account_invoice_line(self, status_type, move, invoice_id, order_id):
        account_obj = self.env['account.account']
        data_line = {
            'invoice_id': invoice_id.id,
            'product_id': move.product_id.id,
            'quantity': move.quantity_done,
            'uom_id': move.product_uom.id
        }

        if status_type == 'purchase':
            account_code = '202100'
            order_line = move.purchase_line_id
            tax_ids = [(6, 0, order_line.taxes_id.mapped('id'))]
            analytic_account_id = order_line.account_analytic_id.id
            data_line.update({
                'purchase_line_id': order_line.id,
            })
        elif status_type == 'sale':
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
