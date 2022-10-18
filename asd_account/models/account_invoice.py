from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _recompute_invoice_tax(self, start_date, end_date, limit=1):
        # if using server action
        invoice_id = self
        # if using cron
        if not invoice_id:
            # Query invoice id with invoice date (only Jan 2022 - Mar 2022)
            query = """
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
                    AND ai."move_name" like 'INV/2022/%'
                    AND ai.state in ('open', 'paid')
                    AND ailt.tax_id = 7
                    AND ai.amount_total != 0
            """
            query += " AND ai.\"date\" BETWEEN '" + start_date + "' AND '" + end_date + "' "
            query += """
                GROUP BY
                    ai.id
                ORDER BY
                    ai."number" ASC
            """
            query += " LIMIT " + str(limit)
            
            self._cr.execute(query)
            result = self._cr.dictfetchall()
            invoice_id = self.env['account.invoice'].search([('id','in',[res['id'] for res in result])])
        for rec in invoice_id:
            # Check date; Check Customer Invoice Tax
            aml_temp = []
            paml_temp = []
            tax_temp = []
            # Unrecon payment that recon with other account_invoice
            for line in rec.payment_move_line_ids:
                if line.journal_id.id == 50:
                    # raise UserError(_(f'This Customer Invoice ({rec.move_id.name}) reconciles with other Customer Invoice ({line.move_id.name}).'))
                    paml_temp.append(line.filtered(lambda p: p.reconciled).id)
                    line.with_context(dict(invoice_id=rec.id)).remove_move_reconcile()
            # Unrecon all payment in this record
            for payment in rec.payment_ids.sorted(lambda p: p.ids):
                aml_temp.append(payment.move_line_ids.filtered(lambda p: p.reconciled).id)
                payment.move_line_ids.with_context(dict(invoice_id=rec.id)).remove_move_reconcile()
                
            # Set to Cancel account_invoice; Set to Draft account_invoice
            rec.action_invoice_cancel()
            rec.action_invoice_draft()
        
            # Force set to Draft; Fix tax to 10%; Validate account_invoice
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
            if paml_temp:
                for paml in paml_temp:
                    rec.assign_outstanding_credit(paml)

    # Replace this method from efaktur module
    @api.one
    def faktur_pajak_create(self):
        if not self.nomor_faktur_id and self.type == 'out_invoice':
            # Query nomor faktur based on invoice id and invoice date (only Jan 2022 - Mar 2022)
            # faktur_id = self.env['nomor.faktur.pajak'].search([('invoice_id', '=', self.id)]).sorted(lambda f: f.id, reverse = True)[0]
            query = """
                SELECT
                    nfp.id
                FROM
                    nomor_faktur_pajak nfp
                LEFT JOIN account_invoice ai ON
                    ai.id = nfp.invoice_id
                WHERE
                    nfp.invoice_id = %s
                    AND nfp.company_id = 5
                    AND nfp.amount_tax = %s
                    AND ai."date" BETWEEN '2022-01-01' AND '2022-03-31'
                ORDER BY
                    nfp.id DESC
                LIMIT 1
            """

            self._cr.execute(query, (self.id, self.amount_tax))
            result = self._cr.dictfetchall()
            faktur_id = self.env['nomor.faktur.pajak'].search([('id','=',result[0]['id'])])
            # Check existing nomor faktur and assign newest nomor faktur to customer invoice
            if faktur_id:
                if faktur_id.amount_tax == self.amount_tax:
                    self.nomor_faktur_id = faktur_id.id
            # Assign new nomor faktur if faktur_id.amount_tax != self.amount_tax
            else:
                obj_no_faktur = self.env['nomor.faktur.pajak'].search([('type','=','out'),('state','=','0'),('invoice_id','=',False),('fp_company_id','=',self.company_id.id)], limit=1)
                if obj_no_faktur:
                    if self.type == 'out_invoice':
                        obj_no_faktur.write({'invoice_id': self.id})
                    self.nomor_faktur_id = obj_no_faktur.id
                else:
                    raise UserError(_('No Faktur Pajak Keluaran found!\nPlease Generate Faktur Pajak Keluaran first!'))
        elif self.nomor_faktur_id:
            obj_no_faktur = self.env['nomor.faktur.pajak'].browse(self.nomor_faktur_id.id)
            if self.nomor_faktur_id and self.type in ('out_invoice','in_invoice'):
                self.nomor_faktur_id.write({'invoice_id': self.id})
        return True