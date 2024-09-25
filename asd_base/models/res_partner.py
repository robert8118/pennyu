# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    id_sfa = fields.Char("ID-SFA")
    show_id_sfa = fields.Boolean(string="Show ID-SFA", compute="_compute_show_id_sfa", default=False)

    @api.depends("company_id")
    def _compute_show_id_sfa(self):
        # Add to list to grant read access to specific Companies.
        # If empty, read access to this field will be granted to all Companies
        filter_showed_company_list = ["CV Perkasa Utama"]
        for rec in self:
            rec.update({"show_id_sfa": False})
            if (not any(filter_showed_company_list)) | (rec.company_id.name in filter_showed_company_list):
                rec.update({"show_id_sfa": True})