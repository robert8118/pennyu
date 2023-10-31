# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    store_grade_id = fields.Many2one('store.grade', string='Store Grade', track_visibility='onchange')
