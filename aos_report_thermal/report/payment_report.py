# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.tools import float_round
from datetime import datetime, date, time, timedelta

class AccountPaymentReportAdmin(models.AbstractModel):
    _name = 'report.aos_report_thermal.attendance_recap_report_view'

    @api.multi
    def get_report_values(self, docids, data=None):
        docss = self.env['account.payment'].browse(docids)
        
        docs = {}
        total_pembayaran = 0.0
        nomor = 0
        docs["listinvoices"] = {}
        partner_id = 0
        for x in docids:
            record = self.env['account.payment'].browse(x)
            partner_id = record.partner_id.id 
            docs['company_id'] = record.company_id
            docs['partner_id'] = record.partner_id
            docs['partner_name'] = record.partner_id.name
            docs['partner_city'] = record.partner_id.city
            docs['invoice_ids'] = record.invoice_ids
            docs['currency_id'] = record.currency_id
            docs['company_image'] = record.company_id.logo
#             print(record.company_id.logo)
#             print("xxxxxxaaaaxxxxxxxx")
            docs['nomor'] = nomor
            for line in record.invoice_ids:
                total_pembayaran = total_pembayaran+record.amount
                saldo = line.residual - record.amount
                due_date = line.date_due
                if due_date:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%y')
                else:
                    due_date = ""
                
                docs["listinvoices"][nomor] = {
                        'nomor_invoice' : line.number,
                        'due_date_invoice' : due_date,
                        'total_invoice' : line.residual,
                        'memo_invoice' : record.communication,
                        'saldo' : line.residual - record.amount,
                        'currency_id' : line.currency_id,
                        'total_pembayaran' : record.amount,
                    }
            
            nomor = nomor+1

        data_invoice = self.env['account.invoice'].search([('partner_id', '=', record.partner_id.id), ('state', '=', 'open')], limit=1)
        info_due_date = data_invoice.date_due
        if info_due_date:
            info_due_date = datetime.strptime(info_due_date, '%Y-%m-%d').strftime('%d/%m/%y')
        else:
            info_due_date = ""
            
        docs["infosaldo"] = {
                'nomor_invoice' : data_invoice.number,
                'due_date_invoice' : info_due_date,
                'total_invoice' : data_invoice.residual,
            }
          
        docs['total_pembayaran'] = total_pembayaran
        
        return {
            'doc_ids': docss.ids,
            'doc_model': 'account.payment',
            'docs': docs,
            'docss': docss,
        }