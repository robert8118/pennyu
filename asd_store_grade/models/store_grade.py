# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital

from odoo import models, fields, api

class StoreGrade(models.Model):
    _name = 'store.grade'
    _description = 'Store Grade'

    name = fields.Char('Name')
    code = fields.Char('Code')
    company_ids = fields.Many2many('res.company', 'store_grade_company_rel', 'store_grade_id', 'company_id', string='Allowed Companies')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            if rec.code:
                res.append((rec.id, '%s' % (rec.code)))
            else:
                res.append((rec.id, '%s' % (rec.name)))
        return res