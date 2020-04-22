# -*- coding: utf-8 -*-
"""FIle for new model discount and inherit purchase"""
from openerp import api, fields, models, _
from odoo.addons import decimal_precision as dp


class DiscountPurchase(models.Model):
    """new class about discount purchase"""
    _name = "discount.purchase"
    _order = "order_line_id"

    order_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line',
        required=True, ondelete='cascade', index=True, copy=False)
    type = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount'),
        ], string='Discount Type', required=True, default='percentage')
    amount = fields.Float(string='Amount Discount', default=0)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def compute_discount_ids(self, discount_ids=False):
        total_disc = 0
        if discount_ids:
            subtotal = 0
            first_discount = discount_ids[0]
            for disc in discount_ids:
                if first_discount.id == disc.id:
                    if disc.type == 'percentage':
                        disc_value = (disc.amount/100)*self.price_unit
                        subtotal = self.price_unit - disc_value
                    elif disc.type == 'fixed':
                        disc_value = disc.amount
                        subtotal = self.price_unit - disc.amount
                    subtotal = subtotal
                    total_disc += disc_value
                else:
                    if disc.type == 'percentage':
                        disc_value = (disc.amount/100)*subtotal
                        subtotal = subtotal - disc_value
                    elif disc.type == 'fixed':
                        disc_value = disc.amount
                        subtotal = subtotal - disc.amount
                    subtotal = subtotal
                    total_disc += disc_value
        if total_disc and self.price_unit:
            percent_discount = (total_disc/self.price_unit)*100
        else:
            percent_discount = 0.0
        return percent_discount

    @api.depends('price_unit', 'purch_discount_ids',
                 'purch_discount_ids.type', 'purch_discount_ids.amount')
    def _compute_net_price(self):
        """function for compute net_price in order line"""
        for line in self:
            percent_discount = line.compute_discount_ids(line.purch_discount_ids)
            tot_disc = (percent_discount/100)*line.price_unit
            line.update({
                'display_discount': tot_disc,
                'net_price': line.price_unit - tot_disc,
            })

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'net_price')
    def _compute_amount(self):
        """replace base function for compute price tax, total, subtotal"""
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id,
                line.product_qty, product=line.product_id,
                partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    display_discount = fields.Float(string='Discount', compute='_compute_net_price',
        digits=dp.get_precision('Discount'), default=0.0, store=True, readonly=True)
    purch_discount_ids = fields.One2many('discount.purchase', 'order_line_id',
        string='Discount Lines')
    net_price = fields.Float(string='Net Unit Price', compute='_compute_net_price',
        store=True, readonly=True, digits=dp.get_precision('Product Price'))


    def action_list_discount(self):
        """function in button for show list of discount"""
        self.ensure_one()
        view = self.env.ref('pn_discount.discount_purchase_order_line_view')

        return {
            'name': _('Discount Order Line'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
            ),
        }

    @api.multi
    def button_discount(self):
        """confirm adding discount"""
        for this in self:
            if this.purch_discount_ids:
                percent_discount = this.compute_discount_ids(this.purch_discount_ids)
                this.discount = percent_discount
            else:
                this.discount = 0.0
        return True

    @api.multi
    def button_apply_all(self):
        """confirm for apply all this discount"""
        for this in self:
            list_disc = []
            if this.purch_discount_ids:
                for disc in this.purch_discount_ids:
                    dict_disc = {}
                    dict_disc['type'] = disc.type
                    dict_disc['amount'] = disc.amount
                    list_disc.append(dict_disc)
            if this.order_id and this.order_id.order_line:
                for line in this.order_id.order_line:
                    if line.id != this.id:
                        if line.purch_discount_ids:
                            for line_disc in line.purch_discount_ids:
                                line_disc.unlink()
                        if list_disc:
                            for add_disc in list_disc:
                                if 'type' in add_disc and 'amount' in add_disc:
                                    self.env['discount.purchase'].create({
                                        'order_line_id' : line.id,
                                        'type' : add_disc['type'],
                                        'amount' : add_disc['amount'],
                                        })
                    line._compute_net_price()
                    line.button_discount()
        return True
