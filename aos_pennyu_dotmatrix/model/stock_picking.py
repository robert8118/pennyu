from odoo import models, api, fields
from datetime import datetime, date, time, timedelta
import math

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.depends('move_lines.price_total')
    def _amount_delivered_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_delivered_untaxed = amount_delivered_tax = 0.0
            for line in order.move_lines:
                amount_delivered_untaxed += line.price_subtotal
                amount_delivered_tax += line.price_tax
            order.update({
                'amount_delivered_untaxed': order.sale_id and order.sale_id.pricelist_id.currency_id.round(amount_delivered_untaxed),
                'amount_delivered_tax': order.sale_id and order.sale_id.pricelist_id.currency_id.round(amount_delivered_tax),
                'amount_delivered_total': amount_delivered_untaxed + amount_delivered_tax,
            })

    amount_delivered_untaxed = fields.Float(string='Untaxed Amount Delivered', readonly=True, compute='_amount_delivered_all', track_visibility='onchange')
    amount_delivered_tax = fields.Float(string='Taxes Delivered', readonly=True, compute='_amount_delivered_all')
    amount_delivered_total = fields.Float(string='Total Delivered', readonly=True, compute='_amount_delivered_all', track_visibility='always')
    due_date = fields.Datetime("Due Date", compute="_compute_due_date")

    def _compute_due_date(self):
        due_date = ''
        for x in self:
            if(x.state == 'done'):
                add_days = x.sale_id.payment_term_id.line_ids.days or 0
                date_done = datetime.strptime(x.date_done,'%Y-%m-%d %H:%M:%S')
                due_date = date_done + timedelta(days=add_days)
            x.due_date = due_date

    @api.multi
    def get_datetime_to_date(self, dt):
        #tmp = '2015-10-28 16:09:59'
        dtd = datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        dd = dtd.date()
        return dd
    
    @api.multi
    def get_move_lines(self, move_lines):
        if len(move_lines) <= 8:
            result = 8
        elif len(move_lines) > 8:
            result = 9
        return result
    
    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Nota')])
        data = tpl.render_template(tpl.body_html, 'stock.picking', self.id)
        self.printer_data = data
        
    @api.multi
    def total_terbilang(self, amount_total):
        """function to converting amount total into word"""
        unit = ["","Satu","Dua","Tiga","Empat",
                "Lima","Enam","Tujuh","Delapan",
                "Sembilan","Sepuluh","Sebelas"]
        result = " "
        total_terbilang = self.total_terbilang
        for line in self:
            n = int(amount_total)
            if n >= 0 and n <= 11:
                result = result + unit[n]
            elif n < 20:
                result = total_terbilang(n % 10) + " Belas"
            elif n < 100:
                result = total_terbilang(n / 10) + " Puluh" + total_terbilang(n % 10)
            elif n < 200:
                result = " Seratus" + total_terbilang(n - 100)
            elif n < 1000:
                result = total_terbilang(n / 100) + " Ratus" + total_terbilang(n % 100)
            elif n < 2000:
                result = " Seribu" + total_terbilang(n - 1000)
            elif n < 1000000:
                result = total_terbilang(n / 1000) + " Ribu" + total_terbilang(n % 1000)
            elif n < 1000000000:
                result = total_terbilang(n / 1000000) + " Juta" + total_terbilang(n % 1000000)
            else:
                result = total_terbilang(n / 1000000000) + " Miliar" + total_terbilang(n % 1000000000)
            return result
        
    def get_company(self):
        return {
            'name': self.company_id.name or '-',
            'street': self.company_id.street or '-',
            'city': self.company_id.city or '-',
            'country': self.company_id.country_id.name or '-',
            'phone': self.company_id.phone or '-',
            'vat': self.company_id.vat or '-'
        }

    def get_partner(self):
        return {
            'display_name': self.partner_id.display_name or '-',
            'street': self.partner_id.street or '-',
            'street2': self.partner_id.street2 or '-',
            'city': self.partner_id.city or '-',
            'country': self.partner_id.country_id.name or ' ',
            'vat': self.partner_id.vat or ' ',
            'is_npwp_pribadi': self.partner_id.is_npwp_pribadi or ' ',
            'nama_npwp_pribadi': self.partner_id.nama_npwp_pribadi or ' ',
            'alamat_npwp_pribadi': self.partner_id.alamat_npwp_pribadi or ' ',
            'npwp': self.partner_id.npwp or ' ',
        }

    def get_shipping(self):
        return {
            'display_name': self.partner_id.display_name or '-',
            'street': self.partner_id.street or '-',
            'street2': self.partner_id.street2 or '-',
            'city': self.partner_id.city or '-',
            'country': self.partner_id.country_id.name or '-',
            'vat': self.partner_id.vat or '-'
        }


    def get_bank(self):
        bank = self.env['account.journal'].search([('company_id', '=', self.company_id.id),('display_on_footer', '=', True)])
        list_b = ''
        for b in bank:
            if b == bank[-1]:
                list_b += b.bank_id.name + ' ' + b.bank_acc_number
            else:
                list_b += b.bank_id.name + ' ' + b.bank_acc_number + ' '
        return list_b

    def get_data(self):
        line_inv = []
        i = 1
        length_p = 50
        length_u = 10
        for line in self.move_lines:
            product_1 = line.product_id.name.replace("'",'')
            product_2 = product_1.replace('"','')
            product_name1 = line.name.replace("'",'')
            space_length_name = (length_p - len(product_name1)) + len(product_name1)
            space_length_p = (length_p - len(product_1)) + len(product_1)
            space_length_u = (length_u - len(line.product_uom.name)) + len(line.product_uom.name)
            line_inv.append({
                'no': i,
                'product': product_1[:length_p],
                'product_name': product_name1[18:],
                'qty': line.quantity_done,
                'prod_name': line.name,
                'uom': line.product_uom.name,
                'price_unit': line.sale_line_id.price_unit,
                'price_subtotal': line.sale_line_id.price_unit * (1 - (line.sale_line_id.discount or 0.0) / 100.0),#line.price_subtotal,
                'discount': line.sale_line_id.discount,
                'price_total': line.price_total,
                'space_length_p': space_length_p,
                'space_length_u': space_length_u
            })
            i += 1
        #print ('---line_inv--',line_inv)
        return line_inv

    def get_datas(self):
        """function for split dotmatrix for maximum 4 lines"""
        line_inv = []
        i = 1
        j = 1
        length_p = 50
        length_u = 10
        split = []
        count_lines = float(len(self.move_lines))
        count_lines = int(math.ceil(count_lines/8))
        index = 1
        # set value of invoice line in list
        for line in self.move_lines:
            product_1 = line.product_id.name.replace("'",'')
            product_2 = product_1.replace('"','')
            product_name1 = line.name.replace("'",'')
            product_name2 = product_name1.replace('"','')
            space_length_name = (length_p - len(product_name1)) + len(product_name1)
            space_length_p = (length_p - len(product_1)) + len(product_1)
            space_length_u = (length_u - len(line.product_uom.name)) + len(line.product_uom.name)
            line_inv.append({
                'no': i,
                'product': product_2[:length_p],
                'product_name': product_name1[18:],
                'qty': line.quantity_done,
                'uom': line.product_uom.name,
                'prod_name': line.name,
                'price_unit': line.sale_line_id.price_unit,
                'price_subtotal': line.price_subtotal,
                'discount': line.sale_line_id.discount,
                'price_total': line.price_total,
                'space_length_p': space_length_p,
                'space_length_u': space_length_u
            })
            i += 1
        # condition for spliting lines
        if line_inv:
            z = []
            if not split:
                # set the 4 lines in page 1
                z.append(line_inv[0])
                z.append(line_inv[1])
                z.append(line_inv[2])
                z.append(line_inv[3])
                z.append(line_inv[4])
                z.append(line_inv[5])
                z.append(line_inv[6])
                z.append(line_inv[7])
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                line_inv.pop(0)
                split.append({'row': j, 'line': z, 'count': count_lines})
                total_line = 0
            if split:
                # set the rest lines in other page with maximum 4 lines
                for sp in split:
                    if count_lines != sp['row']:
                        line = []
                        index = 0
                        for vals in line_inv:
                            if index == 8:
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                if line_inv:
                                    line_inv.pop(0)
                                else:
                                    return split
                                index = 0
                                total_line = 0
                                break
                            total_line += vals['price_total']
                            index += 1
                            line.append(vals)
                        j += 1
                        split.append({'row': j, 'line': line, 'count': count_lines})
        return split

    def terbilang_with_tag(self):
        print ('----amount_delivered_total---',self.amount_delivered_total)
        return '#'+self.total_terbilang(self.amount_delivered_total)+'#'


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.depends('sale_line_id', 'product_uom_qty', 'quantity_done', 'sale_line_id.price_unit', 'sale_line_id.tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            line.update({
                'price_tax': 0, 'price_total': 0,  'price_subtotal': 0,
            })
            if line.sale_line_id:
                price = line.sale_line_id.price_unit * (1 - (line.sale_line_id.discount or 0.0) / 100.0)
                taxes = line.sale_line_id.tax_id.compute_all(price, line.sale_line_id.order_id.currency_id, line.quantity_done, product=line.product_id, partner=line.partner_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes', readonly=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True)
