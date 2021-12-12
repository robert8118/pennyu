# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountMoveLine, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('from_report'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//tree"):
                node.set('default_order', 'move_id desc')
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.multi
    def _get_ending_balance(self):
        ending_balance = self.env.context.get('initial_balance', 0)
        for rec in sorted(self, key=lambda a: (a.move_id.name, a.id)):
            if ending_balance :
                used_currency = self.env.user.company_id.currency_id
                line_debit = rec.company_id.currency_id.compute(rec.debit, used_currency)
                line_credit = rec.company_id.currency_id.compute(rec.credit, used_currency)
                ending_balance = ending_balance + line_debit - line_credit
            rec.ending_balance = ending_balance

    ending_balance = fields.Monetary(compute='_get_ending_balance', currency_field='company_currency_id', string='Balance')
