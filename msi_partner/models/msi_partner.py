# -*- coding: utf-8 -*-
"""file stock picking"""
from odoo import api, models, fields, _


class MSIresPartner(models.Model):
    """inherit model Partner"""
    _inherit = 'res.partner'

    no_ktp = fields.Char('KTP')
    is_npwp_pribadi = fields.Boolean('NPWP Pribadi')
    nama_npwp_pribadi = fields.Char('Nama NPWP Pribadi')
    alamat_npwp_pribadi = fields.Char('Alamat NPWP Pribadi')
    kecataman = fields.Many2one('tbl_kecamatan','Kecamatan')


class MSIkecamatan(models.Model):
    """inherit model Kecamatan"""
    _name = 'tbl_kecamatan'
    name = fields.Char('Nama')
