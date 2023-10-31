# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def check_store_grade(self):
        if self.partner_id:
            active_company_id = self.env.user.company_id
            customer = self.partner_id
            # Validation for Company
            if not customer.parent_id:
                if customer.company_type == 'company':
                    if not customer.store_grade_id:
                        self.partner_id = False
                        raise ValidationError(_('Customer %s has not yet configured Store Grade' % (customer.name)))
                    else:
                        if active_company_id.id not in customer.store_grade_id.company_ids.ids:
                            self.partner_id = False
                            raise ValidationError(_('Company %s is not allowed to transact with customer %s who has Store Grade %s' % (active_company_id.name, customer.name, customer.store_grade_id.code)))
            # Validation for Individual
            else:
                master_customer = customer.parent_id
                master_parent_id = master_customer.company_type == 'company' and not master_customer.parent_id
                if master_parent_id and customer.company_type == 'person':
                    if not master_customer.store_grade_id:
                        self.partner_id = False
                        raise ValidationError(_('The parent customer of this customer (%s) has not yet configured Store Grade' % (master_customer.name)))
                    else:
                        if active_company_id.id not in master_customer.store_grade_id.company_ids.ids:
                            self.partner_id = False
                            raise ValidationError(_("Company %s is not allowed to transact with customer %s because this customer's parent (%s) has Store Grade %s" % (active_company_id.name, customer.name, master_customer.name, master_customer.store_grade_id.code)))

