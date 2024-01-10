# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital

from odoo import api, fields, models, tools, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    @api.onchange('npwp')
    def onchange_npwp(self):
        res = {}
        vals = {}
        npwp = self.npwp
        if not npwp:
            return
        elif len(npwp) == 20:
            self.npwp = npwp
        elif len(npwp) == 15:
            formatted_npwp = npwp[:2] + '.' + npwp[2:5] + '.' + npwp[5:8] + '.' + npwp[8:9] + '-' + npwp[9:12] + '.' + npwp[12:15]
            self.npwp = formatted_npwp
        elif len(npwp) == 16:
            formatted_npwp = npwp[:2] + '.' + npwp[2:5] + '.' + npwp[5:8] + '.' + npwp[8:9] + '-' + npwp[9:12] + '.' + npwp[12:16]
            self.npwp = formatted_npwp
        else:
            warning = {
                'title': _('Warning'),
                'message': _('Wrong Format! Must 15 or 16 digit'),
            }
            return {'warning': warning, 'value' : {'npwp' : False}}
        return res
