# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    id_sfa = fields.Char("ID-SFA")
    show_id_sfa = fields.Boolean(string="Show ID-SFA", compute="_compute_show_id_sfa", default=False)

    @api.depends("name", "partner_id.name")
    def _compute_show_id_sfa(self):
        selected_company = self._get_selected_company(filtered_companies_list=["CV Perkasa Utama"])
        for rec in self:
            rec.update({"show_id_sfa": False})
            match_company = (rec.name in selected_company) and (rec.partner_id.name in selected_company)
            # If not use filtered, show this field for all companies
            if match_company or not any(selected_company):
                rec.update({"show_id_sfa": True})

    def _get_selected_company(self, filtered_companies_list=[]):
        result = []
        if not any(filtered_companies_list):
            return result
        else:
            company_obj = self.env["res.company"]
            for company in filtered_companies_list:
                company_ids = company_obj.search([("name", "like", company)])
                if company_ids:
                    result.extend(company_ids.mapped("name"))
            return result