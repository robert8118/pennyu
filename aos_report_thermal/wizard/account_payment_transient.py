from odoo import models, api, fields
from datetime import datetime, date, time, timedelta
import math
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentTransient(models.TransientModel):
    _name = "account.payment.transient"


    @api.multi
    def printReportThermal(self):
        print("aaaaaaaaaaaaaaaa")
        active_ids = self.env.context.get('active_ids', [])
        print(active_ids)
        active_record = self._context['active_id']
#         print(active_record)
        record = self.env['account.payment'].browse(active_record)
#         print(record)

        data = {
#             'ids': self.ids,
            'model': "account.payment",
#             'record': record.id,
        }
    
        total_pembayaran = 0.0
        for x in active_ids:
            record = self.env['account.payment'].browse(x)
#             print("Partner Id",record.partner_id)
            data['partner_id'] = record.partner_id
            data['partner_name'] = record.partner_id.name
            data['partner_city'] = record.partner_id.city
            data['invoice_ids'] = record.invoice_ids
#             print("Partner Name",record.partner_id.name)
#             print("Partner City",record.partner_id.city)
            for line in record.invoice_ids:
                print("Nomor Invoice",line.number)
                print("Date Invoice",line.date_due)
                print("Total Invoice",line.residual)
                print("Memo",record.communication)
                total_pembayaran = total_pembayaran+record.amount
                saldo = line.residual - record.amount
#                 print("Saldo",line.residual - record.amount)
#                 data['data_pembayaran_nota'] = {
#                     'nomor_invoice' : line.number,
#                     'due_date_invoice' : line.date_due,
#                     'total_invoice' : line.residual,
#                     'memo_invoice' : record.communication,
#                     'saldo_invoice' : saldo,
#                 }
#             data_invoice = self.env['account.invoice'].search([('partner_id', '=', record.partner_id.id), ('state', '=', 'open')])
#             print("data invoice",data_invoice)
#             print("data Number",data_invoice.number)
#             print("Total Invoice",data_invoice.residual)
        
        data['total_pembayaran'] = total_pembayaran
        print("Total Pembayaran",total_pembayaran)
        
        data['model'] = 'account.payment'
        print(data)
        return self.env.ref('aos_report_thermal.action_report_payment_admin').report_action(self, data=data)
    
    
# class AccountPaymentReportAdmin(models.AbstractModel):
#     _name = 'report.aos_report_thermal.report_payment'
#  
#     @api.multi
#     def get_report_values(self, docids, data=None):
#         print("xxxxxaaaaxxxxx----",docids)
#         docs = self.env['account.payment'].browse(docids)
#         return {
#             'doc_ids': docs.ids,
#             'doc_model': 'account.payment',
#             'docs': docs
#         }
