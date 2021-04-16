from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def auto_invoice(self, picking_id=None):
        if self:
            sp_id = self
        else:
            sp_id = picking_id
        if sp_id.group_id:

            if sp_id.picking_type_id.code == 'incoming':
                po = self.env['purchase.order'].search([('name', '=', sp_id.group_id.name)])
                origin = po.name
                payment_term_id = po.payment_term_id.id
                company_id = po.company_id.id
                journal_id = self.env['account.journal'].search(
                    [('type', '=', 'purchase'),
                     ('company_id', '=', company_id)])
                journal_id = journal_id[0].id
                account_id = self.env['account.account'].search(
                    [('internal_type', '=', 'payable'),
                     ('company_id', '=', company_id),
                     ('deprecated', '=', False)])
                account_id = account_id[0].id
            data = {
                'type': 'in_invoice',
                'journal_type': 'purchase',
                'release_to_pay': 'yes',
                'partner_id': sp_id.partner_id.id,
                'payment_term_id': payment_term_id,
                'account_id': account_id,
                'journal_id': journal_id,
                'company_id': company_id,
                'origin': origin,
                'user_id': self._uid,
            }
            inv = self.env['account.invoice'].create(data)
            for move in sp_id.move_lines:
                if move.quantity_done:
                    if move.product_id.default_code:
                        product_name = '%s: [%s] %s' % (po.name, move.product_id.default_code, move.product_id.name)
                    else:
                        product_name = '%s: %s' % (po.name, move.product_id.name)
                    data_line = {
                        'invoice_id': inv.id,
                        'product_id': move.product_id.id,
                        'quantity': move.quantity_done,
                        'uom_id': move.purchase_line_id.product_uom.id,
                        'account_id': self.env['account.account'].search(
                            [('code', '=', '202100'), ('company_id', '=', company_id)]).id,
                        'name': product_name,
                        'price_unit': move.purchase_line_id.price_unit,
                        'purchase_line_id': move.purchase_line_id.id,
                        'account_analytic_id': move.purchase_line_id.account_analytic_id.id,
                        'invoice_line_tax_ids': move.purchase_line_id.taxes_id,
                    }
                    self.env['account.invoice.line'].create(data_line)
            return inv
        else:
            return False

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.picking_type_id.code in ['incoming']:
            self.auto_invoice()
        return res


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        res = super(StockBackorderConfirmation, self).process()
        # if self.pick_ids.picking_type_id.code in ['incoming']:
        #     self.env['stock.picking'].auto_invoice(self.pick_ids)
        return res
