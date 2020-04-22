# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class msi_invoice(models.Model):
    _inherit = 'account.invoice'

    status_penagihan1 = fields.Float('Status Penagihan', default=0)
    bg = fields.Text('BG')






