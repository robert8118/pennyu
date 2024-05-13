# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    is_limit_requested_date_change = fields.Boolean('Is Limit Requested Date Change?')
    limit_requested_date_change = fields.Integer('Limit Requested Date Change')