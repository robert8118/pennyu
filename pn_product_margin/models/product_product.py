from odoo import api, fields, models
import time


class ProductProduct(models.Model):
    _inherit = 'product.product'

    actual_margin = fields.Float(compute='_compute_product_margin_fields_values', string='Actual Margin',
                                 help="Turnover - Total actual cost")

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

            res[val.id]['actual_margin'] = res[val.id]['turnover'] - result_cost[0] if result_cost[0] else 0
            for k, v in res[val.id].items():
                setattr(val, k, v)
        return res
