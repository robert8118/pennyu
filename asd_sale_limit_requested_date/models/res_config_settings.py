# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_limit_requested_date_change = fields.Boolean(related='company_id.is_limit_requested_date_change')
    limit_requested_date_change = fields.Integer(related='company_id.limit_requested_date_change')