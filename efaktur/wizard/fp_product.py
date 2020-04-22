import logging
import time

import base64, itertools, csv, codecs, io, sys

from odoo import api, fields, models, _
from odoo.modules import get_module_path
from odoo.exceptions import UserError

from .csv_reader import UnicodeWriter

_logger = logging.getLogger(__name__)


class fp_product_export(models.TransientModel):
    _name = 'fp.product.export'
    _description = 'Export E-Faktur Product'

    data = fields.Binary('Download', readonly=True)
    filename = fields.Char('File Name', size=32)
    
    @api.multi
    def action_export(self):
        file_data = io.StringIO()
        rows = self.get_data()
        try:
            writer = UnicodeWriter(file_data)
            writer.writerows(rows)
            file_value = file_data.getvalue()
            self.write({'data': base64.encodestring((file_value).encode()).decode(),
                        'filename': 'Efaktur OB.csv'})
        finally:
            file_data.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fp.product.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    
    def _get_products(self, headers):
        context = dict(self._context or {})
        products = self.env['product.product'].browse(context.get('active_ids'))
        rows = []
        for prod in products:
            data = {
                    'OB'        : 'OB',
                    'KODE_OBJEK': prod.default_code or '',
                    'NAMA'      : prod.name,
                    'HARGA_SATUAN': prod.list_price
                }
            
            row = [data[i] for i in headers]
            rows.append(list(row))
            
            prod.fp_export=True
            prod.fp_date=time.strftime("%Y-%m-%d %H:%M:%S")
        return rows
        
    def get_data(self, context=None):
        headers = ['OB','KODE_OBJEK','NAMA','HARGA_SATUAN']
        
        get_products_func = getattr(self, ("_get_products"), None)
        products = get_products_func(headers)
        rows = itertools.chain(
                               (headers,),
                               products
                               )
        return rows
    
#     @api.multi
#     def action_exportx(self):
#         context = dict(self._context or {})
#         cr = self.env.cr
#         headers = ['OB','KODE_OBJEK','NAMA','HARGA_SATUAN']
# 
#         mpath = get_module_path('efaktur')
# 
#         csvfile = open(mpath + '/static/export/fp_product.csv', 'wt')
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow([h.upper() for h in headers])
# 
#         products = self.env['product.product'].browse(context.get('active_ids'))
#         i=0
#         for prod in products:
#             data = {
#                 'OB'        : 'OB',
#                 'KODE_OBJEK': prod.default_code or '',
#                 'NAMA'      : prod.name,
#                 'HARGA_SATUAN':prod.list_price
#             }
#             csvwriter.writerow([data[v] for v in headers])
#             prod.fp_export=True
#             prod.fp_date=time.strftime("%Y-%m-%d %H:%M:%S")
#             i+=1
# 
#         cr.commit()
#         csvfile.close()
# 
#         raise UserError("Export %s record(s) Done!" % i)
