from odoo import models, fields, api
from datetime import date

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def _recompute_invoice_tax(self):
        self._cr.execute("""
            SELECT
                ai.id
            FROM
                account_invoice ai
            LEFT JOIN account_invoice_line ail ON
                ai.id = ail.invoice_id
            LEFT JOIN account_invoice_line_tax ailt ON
                ailt.invoice_line_id = ail.id
            WHERE
                ai.company_id = 5
                AND ai."number" like 'INV/2022/%'
                AND ai.state in ('open', 'paid')
                AND ai."date" between '2022-01-01' AND '2022-03-31'
                AND ailt.tax_id = 7
                AND ai.amount_total != 0
            GROUP BY
                ai.id
            ORDER BY
                ai."number" ASC
            LIMIT 1;""")

        ai_id = self._cr.fetchall()
        invoice_id = self.env['account.invoice'].search([('id', '=', [ai[0] for ai in ai_id][0])])
        for rec in invoice_id:
            # Check date; Check Customer Invoice Tax
            # tax_percent = float('%.5f' % (100 * rec.amount_tax / rec.amount_untaxed))
            # date_temp = [int(i) for i in rec.date.split("-")]
            # is_date_range = date(2022, 1, 1) < date(date_temp[0], date_temp[1], date_temp[2]) < date(2022, 3, 31)
            # if (rec.company_id.id == 5) and (is_date_range) and (rec.state in ('open','paid')) and (tax_percent != 10.000):
            faktur_temp = rec.nomor_faktur_id
            aml_temp = []
            tax_temp = []
            # Unrecon all payment in this account_invoice record
            for payment in rec.payment_ids.sorted(lambda p: p.ids):
                aml_temp.append(payment.move_line_ids.filtered(lambda p: p.reconciled).id)
                payment.move_line_ids.with_context(dict(invoice_id=rec.id)).remove_move_reconcile()
                
            # Set to Cancel account_invoice; Set to Draft account_invoice
            rec.action_invoice_cancel()
            rec.action_invoice_draft()
        
            # Force set to Draft; Replace tax 11% to 10%; Validate account_invoice
            if rec.state == 'open':
                rec.write({'state': 'draft'})
            for line in rec.invoice_line_ids:
                tax_temp = line.invoice_line_tax_ids.ids
                if tax_temp and 7 in tax_temp:
                    for i in range(len(tax_temp)):
                        if tax_temp[i] == 7:
                            tax_temp[i] = 16
                    line.write({
                    'invoice_line_tax_ids': [(6, 0, tax_temp)],
                    })
            rec.action_invoice_open()
            
            # Reconcile account_invoice
            for aml in aml_temp:
                rec.assign_outstanding_credit(aml)