
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.depends('order_line.price_delivered_total')
    def _amount_delivered_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_delivered_untaxed = amount_delivered_tax = 0.0
            for line in order.order_line:
                amount_delivered_untaxed += line.price_delivered_subtotal
                amount_delivered_tax += line.price_delivered_tax
            order.update({
                'amount_delivered_untaxed': order.pricelist_id.currency_id.round(amount_delivered_untaxed),
                'amount_delivered_tax': order.pricelist_id.currency_id.round(amount_delivered_tax),
                'amount_delivered_total': amount_delivered_untaxed + amount_delivered_tax,
            })
            
    

    amount_delivered_untaxed = fields.Monetary(string='Untaxed Amount Delivered', store=True, readonly=True, compute='_amount_delivered_all', track_visibility='onchange')
    amount_delivered_tax = fields.Monetary(string='Taxes Delivered', store=True, readonly=True, compute='_amount_delivered_all')
    amount_delivered_total = fields.Monetary(string='Total Delivered', store=True, readonly=True, compute='_amount_delivered_all', track_visibility='always')
    date_due = fields.Date(string='Due Date',
        readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False,
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. The Payment terms may compute several due dates, for example 50% "
             "now and 50% in one month, but if you want to force a due date, make sure that the payment "
             "term is not set on the invoice. If you keep the Payment terms and the due date empty, it "
             "means direct payment.")
    
    @api.onchange('payment_term_id', 'date_order')
    def _onchange_payment_term_date_order(self):
        date_order = self.date_order
        if not date_order:
            date_order = fields.Date.context_today(self)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_order)[0]
            self.date_due = max(line[0] for line in pterm_list)
        elif self.date_due and (date_order > self.date_due):
            self.date_due = date_order
            
    @api.multi
    def print_nota(self):
        return self.env.ref('aos_sale_nota_invoice.action_report_saleorder_nota').report_action(self)
    
    
#     @api.multi
#     def total_terbilang(self, amount_total):
#         """function to converting amount total into word"""
#         unit = ["","Satu","Dua","Tiga","Empat",
#                 "Lima","Enam","Tujuh","Delapan",
#                 "Sembilan","Sepuluh","Sebelas"]
#         result = " "
#         total_terbilang = self.total_terbilang
#         for line in self:
#             n = int(amount_total)
#             if n >= 0 and n <= 11:
#                 result = result + unit[n]
#             elif n < 20:
#                 result = total_terbilang(n % 10) + " Belas"
#             elif n < 100:
#                 result = total_terbilang(n / 10) + " Puluh" + total_terbilang(n % 10)
#             elif n < 200:
#                 result = " Seratus" + total_terbilang(n - 100)
#             elif n < 1000:
#                 result = total_terbilang(n / 100) + " Ratus" + total_terbilang(n % 100)
#             elif n < 2000:
#                 result = " Seribu" + total_terbilang(n - 1000)
#             elif n < 1000000:
#                 result = total_terbilang(n / 1000) + " Ribu" + total_terbilang(n % 1000)
#             elif n < 1000000000:
#                 result = total_terbilang(n / 1000000) + " Juta" + total_terbilang(n % 1000000)
#             else:
#                 result = total_terbilang(n / 1000000000) + " Miliar" + total_terbilang(n % 1000000000)
#             return result
        
    @api.multi
    def currency_word(self):
        """function to converting currency into word"""
        result = " "
        for cr in self:
            if cr.currency_id.name == 'USD':
                result = " Dollar"
            elif cr.currency_id.name == 'EUR':
                result = " Euro"
            elif cr.currency_id.name == 'JPY':
                result = " Yen"
            elif cr.currency_id.name == 'IDR':
                result = " Rupiah"
            else:
                result = " "
            return result
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_uom_qty', 'qty_delivered', 'discount', 'price_unit', 'tax_id')
    def _compute_delivered_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.qty_delivered, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_delivered_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_delivered_total': taxes['total_included'],
                'price_delivered_subtotal': taxes['total_excluded'],
            })
            
    
    price_delivered_subtotal = fields.Monetary(compute='_compute_delivered_amount', string='Subtotal Delivered', readonly=True, store=True)
    price_delivered_tax = fields.Float(compute='_compute_delivered_amount', string='Taxes Delivered', readonly=True, store=True)
    price_delivered_total = fields.Monetary(compute='_compute_delivered_amount', string='Total Delivered', readonly=True, store=True)