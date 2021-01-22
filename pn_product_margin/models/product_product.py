from odoo import api, fields, models
import time


class ProductProduct(models.Model):
    _inherit = 'product.product'

    actual_margin = fields.Float(compute='_compute_product_margin_fields_values', string='Actual Margin',
                                 help="Turnover - Total actual cost")
    actual_cost = fields.Float(compute='_compute_product_margin_fields_values', string='Actual Cost',
                               help="Get cost from HPP")
    pos_avg_price = fields.Float(compute='_compute_product_margin_fields_values', string='Avg. Unit Price')
    pos_num_invoiced = fields.Float(compute='_compute_product_margin_fields_values', string='# Posted in POS Order')
    pos_gap = fields.Float(compute='_compute_product_margin_fields_values', string='POS Order Gap')
    pos_turnover = fields.Float(compute='_compute_product_margin_fields_values', string='Turnover')
    pos_expected = fields.Float(compute='_compute_product_margin_fields_values', string='Expected Sale')

    def _compute_product_margin_fields_values(self, field_names=None):
        res = super(ProductProduct, self)._compute_product_margin_fields_values(field_names=None)
        for val in self:
            date_from = self.env.context.get('date_from', time.strftime('%Y-01-01'))
            date_to = self.env.context.get('date_to', time.strftime('%Y-12-31'))
            invoice_state = self.env.context.get('invoice_state', 'open_paid')
            res[val.id]['date_from'] = date_from
            res[val.id]['date_to'] = date_to
            res[val.id]['invoice_state'] = invoice_state
            invoice_types = ()
            states = ()
            if invoice_state == 'paid':
                states = ('paid',)
            elif invoice_state == 'open_paid':
                states = ('open', 'paid')
            elif invoice_state == 'draft_open_paid':
                states = ('draft', 'open', 'paid')
            if "force_company" in self.env.context:
                company_id = self.env.context['force_company']
            else:
                company_id = self.env.user.company_id.id

            sqlstr_cost = """
                select
                    sum(aml.debit) as total_actual_cost
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join account_move am on (am.id = i.move_id)
                left join account_move_line aml on (aml.move_id = am.id)
                left join account_account aa on (aml.account_id = aa.id)
                where l.product_id = %s
                    and i.state in %s
                    and i.type IN %s
                    and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                    and aml.product_id = l.product_id
                    and aa.user_type_id = 17
                """

            invoice_types = ('out_invoice', 'in_refund')
            self.env.cr.execute(sqlstr_cost, (val.id, states, invoice_types, date_from, date_to, company_id))
            result_cost = self.env.cr.fetchall()[0]

            res[val.id]['actual_cost'] = result_cost[0] if result_cost[0] else 0
            res[val.id]['actual_margin'] = res[val.id]['turnover'] - res[val.id]['actual_cost']

            sqlstr_pos = """
                            select
                                sum(pol.qty) as pos_num_invoiced,
                                sum(pol.price_unit * pol.qty)/nullif(sum(pol.qty),0) as pos_avg_price,
                                sum(pol.qty * pt.list_price) as pos_expected,
                                sum(pol.qty * (pol.price_subtotal/(nullif(pol.qty,0)))) as pos_turnover
                            from pos_order_line pol
                            left join product_product pp on (pp.id=pol.product_id)
                            left join product_template pt on (pt.id = pp.product_tmpl_id)
                            where pol.product_id = %s
                            """

            self.env.cr.execute(sqlstr_pos, (val.id,))
            result_pos = self.env.cr.fetchall()[0]

            res[val.id]['pos_num_invoiced'] = result_pos[0] if result_pos[0] else 0
            res[val.id]['pos_avg_price'] = result_pos[1] if result_pos[1] else 0
            res[val.id]['pos_expected'] = result_pos[2] if result_pos[2] else 0
            res[val.id]['pos_turnover'] = result_pos[3] if result_pos[3] else 0
            res[val.id]['pos_gap'] = res[val.id]['pos_expected'] - res[val.id]['pos_turnover']

            for k, v in res[val.id].items():
                setattr(val, k, v)
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    price_subtotal = fields.Float(compute='_compute_amount_line_all', digits=0, string='Subtotal w/o Tax', store=True)
