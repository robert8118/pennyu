# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from openerp.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    requested_date = fields.Datetime(track_visibility='onchange')

    @api.multi
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        self._limit_requested_date_change()
        return res

    def _limit_requested_date_change(self):
        # Get requested date chatter
        mail_obj = self.env['mail.message']
        mail_domain = [('model', '=', self._name), ('parent_id.res_id', '=', self.id)]
        mail_id = mail_obj.search(mail_domain).filtered(lambda m: any(m.tracking_value_ids) and 'requested_date' in m.mapped('tracking_value_ids.field'))

        # Limit requested date based on configuration
        company_id = self.company_id or self.env.user.company_id
        is_change_limit = company_id.is_limit_requested_date_change
        change_limit = company_id.limit_requested_date_change
        if is_change_limit:
            if change_limit <= 0:
                raise ValidationError(f"Requested Date limit cannot be made more than {change_limit}")
            elif len(mail_id) > change_limit:
                raise ValidationError(f"Requested Date changes cannot be made more than {change_limit} times")