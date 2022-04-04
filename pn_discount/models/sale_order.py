# -*- coding: utf-8 -*-
"""FIle for new model discount and inherit sale"""
from odoo import api, models, fields, _
from odoo.addons import decimal_precision as dp

class DiscountSale(models.Model):
    """new class discount sale"""
    _name = "discount.sale"
    _order = "order_line_id"

    order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line',
        readonly=True, required=True, ondelete='cascade', index=True, copy=False)
    type = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount'),
        ], string='Discount Type', required=True, default='percentage')
    amount = fields.Float(string='Amount Discount', default=0)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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


    @api.depends('price_unit', 'sale_discount_ids')
    def _compute_net_price(self):
        """function for compute net_price in order line"""
        for line in self:
            if line.sale_discount_ids :
                percent_discount = line.compute_discount_ids(line.sale_discount_ids)
                tot_disc = (percent_discount/100)*line.price_unit
                line.update({
                    'display_discount': tot_disc,
                    'net_price': line.price_unit - tot_disc,
                })


    display_discount = fields.Float(string='Discount', compute='_compute_net_price',
        digits=dp.get_precision('Discount'), default=0.0, store=True, readonly=True)
    sale_discount_ids = fields.One2many('discount.sale', 'order_line_id',
        string='Discount Lines', copy=True, auto_join=True)
    net_price = fields.Float(string='Net Unit Price', compute='_compute_net_price',
        store=True, readonly=True, digits=dp.get_precision('Product Price'))

    def action_list_discount(self):
        """Add Action view discount to show list discount"""
        self.ensure_one()
        view = self.env.ref('pn_discount.discount_sale_order_line_view')

        return {
            'name': _('Discount Sale Order Line'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
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
            if this.sale_discount_ids:
                percent_discount = this.compute_discount_ids(this.sale_discount_ids)
                this.discount = percent_discount
        return True

    @api.multi
    def button_apply_all(self):
        """confirm for apply all this discount"""
        for this in self:
            list_disc = []
            if this.sale_discount_ids:
                for disc in this.sale_discount_ids:
                    dict_disc = {}
                    dict_disc['type'] = disc.type
                    dict_disc['amount'] = disc.amount
                    list_disc.append(dict_disc)
            if this.order_id and this.order_id.order_line:
                for line in this.order_id.order_line:
                    if line.id != this.id:
                        if line.sale_discount_ids:
                            for line_disc in line.sale_discount_ids:
                                line_disc.unlink()
                        if list_disc:
                            for add_disc in list_disc:
                                if 'type' in add_disc and 'amount' in add_disc:
                                    self.env['discount.sale'].create({
                                        'order_line_id' : line.id,
                                        'type' : add_disc['type'],
                                        'amount' : add_disc['amount'],
                                        })
                    line._compute_net_price()
                    line.button_discount()
        return True

    @api.model
    def create(self, values):
        discount = values.get('discount')
        res = super(SaleOrderLine, self).create(values)
        # setelah res discount jadi hilang
        if not values.get('discount') and not res.sale_discount_ids and discount :
            res.discount = discount
        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, values):
        return super(SaleOrder, self).create(values)
