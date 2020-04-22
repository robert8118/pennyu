# -*- coding: utf-8 -*-
##############################################################################
#
#    DevIntelle Solution(Odoo Expert)
#    Copyright (C) 2015 Devintelle Soluation (<http://devintelle.com/>)
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp.exceptions import except_orm

from odoo import models, fields, api

from odoo.tools.misc import str2bool, xlwt
from xlsxwriter.workbook import Workbook
import base64
from io import BytesIO
from xlwt import easyxf
import csv


class inventory_wizard(models.TransientModel):  

    _name = 'inventory.age.wizard'
    _description = 'Stock Ageing Report'

    period_length = fields.Integer('Period Length (days)', default=30)
    product_id = fields.Many2many('product.product', string='Product')
    product_category_id = fields.Many2one('product.category', 'Product Category')
    company_id = fields.Many2one('res.company', 'Company')
    date_from = fields.Date('Date', default=lambda *a: time.strftime('%Y-%m-%d'))
    location_ids = fields.Many2many('stock.location',string='Location')

    def _print_report(self, data):
        res = {}

        period_length = data['form']['period_length']
        if period_length <= 0:
            raise except_orm(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise except_orm(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        for i in range(7)[::-1]:
            stop = start - relativedelta(days=period_length)
            res[str(i)] = {
                'name'  : (i != 0 and (str((7 - (i + 1)) * period_length) + '-' + str((7 - i) * period_length)) or ('+' + str(6 * period_length))),
                'stop'  : start.strftime('%Y-%m-%d'),
                'start' : (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
            
        data['form'].update(res)

        return self.env.ref('dev_inventory_ageing_report.action_report_aged_inventory').report_action(self, data=data)


    @api.multi
    def check_report(self):
        data = {}
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        for record in self:
            data['form']  = self.read(['period_length', 'product_id', 'product_category_id', 'company_id', 'date_from','location_ids'])[0]
        return self._print_report(data)
        
        
    @api.multi
    def get_location_name(self,location_ids):
        location_pool=self.env['stock.location']
        name = ''
        for location in location_pool.browse(location_ids):
            if name:
                name = name + ','+location.name
            else:
                name = location.name
        return name

    @api.model
    def get_lines(self, form):
        res = []
        product_ids=[]
        quant_obj = self.env.get('stock.quant')
        product_category_id = form['product_category_id'][0]
        product_obj = self.env['product.product']
        if product_category_id:
            products = product_obj.search([('categ_id', 'child_of',[product_category_id])])
            product_ids = products._ids
        if form.get('product_id'):
            wizard_product_id = form['product_id']
            product_ids = wizard_product_id
            
            
        for product in product_obj.browse(product_ids):
            product_dict = {
                'pname': product.name
            }
            location_id = form['location_ids']
                
            date_from = form['date_from']
            # warehouse = form['warehouse_id'][0]
            ctx = self._context.copy()
            ctx.update({
                'location': location_id,
                'from_date': date_from,
                'to_date': date_from
            })
            product_qty = product._product_available(False, False)
            qty_list = product_qty.get(product.id)
            product_dict.update({
                'onhand_qty' : qty_list['qty_available'],
            })
            for data in range(0, 7):
                total_qty = 0
                if form.get(str(data)):
                    start_date = form.get(str(data)).get('start')
                    stop_date = form.get(str(data)).get('stop')
                    if not start_date:
                        domain = [('create_date', '<=', stop_date), ('location_id', 'in', location_id),
                                  ('product_id', '=', product.id)]
                    else:
                        domain = [('create_date', '<=', stop_date), ('create_date', '>=', start_date),
                                  ('location_id', 'in', location_id), ('product_id', '=', product.id)]

                    for quant in quant_obj.search(domain):
                        total_qty += quant.quantity
                    product_dict[str(data)] = total_qty
            res.append(product_dict)
        return res
    
    def _print_exp_report(self, data):
        res = {}
        period_length = data['form']['period_length']
        if period_length <= 0:
            raise except_orm(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise except_orm(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        for i in range(7)[::-1]:
            stop = start - relativedelta(days=period_length)
            res[str(i)] = {
                'name': (i != 0 and (str((7 - (i + 1)) * period_length) + '-' + str((7 - i) * period_length)) or ('+' + str(6 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        import base64
        filename='Inventory Ageing Report.xls'
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Inventory Ageing Report')
        
        header_style= easyxf('font:height 200;pattern: pattern solid, fore_color black; align: horiz center;font: color white; font:bold True;' "borders: top thin,left thin,right thin,bottom thin")
        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        text_center = easyxf('font:height 200; align: horiz center;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin")
        
        
        first_col = worksheet.col(0)
        second_col = worksheet.col(1)
        third_col = worksheet.col(2)
        four_col = worksheet.col(3)
        
        five_col = worksheet.col(4)
        six_col = worksheet.col(5)
        seven_col = worksheet.col(6)
        eight_col = worksheet.col(7)
        nine_col = worksheet.col(8)
        ten_col = worksheet.col(9)
        eleven_col = worksheet.col(10)
        
        
        
        first_col.width = 130 * 30
        second_col.width = 150 * 30
        third_col.width = 180 * 30
        four_col.width = 130 * 30
        five_col.width = 150 * 30
        six_col.width = 130 * 30
        seven_col.width = 130 * 30
        eight_col.width = 130 * 30
        nine_col.width = 130 * 30
        ten_col.width = 130 * 30
        eleven_col.width = 130 * 30
        
        
        worksheet.write_merge(0, 1, 0, 3, 'Inventory Ageing Report',easyxf('font:height 400; align: horiz center;font:bold True;' "borders: top thin,bottom thin , left thin, right thin"))
        date_from = data['form']['date_from'] or ' '
        if date_from:
            date = datetime.strptime(date_from.split(' ')[0], '%Y-%m-%d')
            date_from = date.strftime('%d-%m-%Y')
            worksheet.write(2,4,'Start Date'+ '-'+str(date_from))
        worksheet.write(5,0, 'Product',header_style)
        worksheet.write(5,1, data['form']['6']['name'],header_style)
        worksheet.write(5,2, data['form']['5']['name'],header_style)
        worksheet.write(5,3, data['form']['4']['name'],header_style)
        worksheet.write(5,4, data['form']['3']['name'],header_style)
        worksheet.write(5,5, data['form']['2']['name'],header_style)
        worksheet.write(5,6, data['form']['1']['name'],header_style)
        worksheet.write(5,7, data['form']['0']['name'],header_style)
        line = self.get_lines(data['form'])
        if line:
            i=6
            p=0
            for product in line:
                if product.get('onhand_qty', 0) and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,0, product['pname'])
                    
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,1, product['6'])   
                    
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,2, product['5'])   
                    
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,3, product['4'])
                
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0) or product['5'] > 0 or product['6'] > 0:
                    p+=1
                    worksheet.write(i,4, product['3'])
                    
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,5, product['2'])
                                
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,6, product['1'])
                if product.get('onhand_qty', 0) != 0 and product.get('onhand_qty', 0) > 0 and (product['0'] > 0 or product['1'] > 0 or product['2'] > 0 or product['3'] > 0 or product['4'] > 0 or product['5'] > 0 or product['6'] > 0):
                    p+=1
                    worksheet.write(i,7, product['0'])
                if p > 0:
                    i+=1
                p=0
                     
        
        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['inventory.age.dow'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'inventory.age.dow',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            
        }
        
        
    def inventory_age_history_excel(self):
        
        data = {}
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        for record in self:
            data['form']  = self.read(['period_length', 'product_id', 'product_category_id', 'location_ids', 'company_id', 'date_from'])[0]
        return self._print_exp_report(data)
        

class inventory_age_dow(models.TransientModel):
    _name= "inventory.age.dow"
    
    excel_file = fields.Binary('Excel Report ')
    file_name = fields.Char('Excel File', size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
