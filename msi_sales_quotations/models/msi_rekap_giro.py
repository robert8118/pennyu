# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_rekap_giro(models.Model):
    _name = 'tbl_rekap_giro'

    name = fields.Many2one('res.partner','Customer', required=True)
    nama_bank = fields.Many2one('tbl_acc_bank','Nama Bank', required=True)
    no_bg = fields.Char('Nomer BG') 
    tgl_bg = fields.Date('Tanggal BG') 
    nilai_bg = fields.Float('Nilai BG', sum='Total BG')

    no_invoice = fields.Many2one('account.invoice','No Invoice', required=True)
    tgl_invoice = fields.Date('Tanggal Invoice') 
    nilai_invoice = fields.Float('Nilai Invoice', sum='Total')  

    tgl_setor = fields.Date('Tanggal Setor')
    setor_ke = fields.Many2one('tbl_acc_norek','Penyetoran')
    nilai_setor = fields.Float('Nilai Setor', sum='Total')
    tgl_masuk = fields.Date('Tanggal Masuk Rek Koran') 
    ket = fields.Char('Keterangan') 
    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr', 'To Approve'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.onchange('no_invoice')
    def onchange_no_invoice(self):
        if self.no_invoice:
            self.nilai_invoice = self.no_invoice.amount_total 
            self.tgl_invoice = self.no_invoice.date_invoice 


    def act_set(self):
      if not self.nama_bank:
         raise UserError(_('Nama Bank Giro Belum Diisi'))

      if not self.no_bg:
         raise UserError(_('Nomer Giro Belum Diisi'))

      if not self.tgl_bg:
         raise UserError(_('Tanggal Giro Belum Diisi'))

      if not self.nilai_bg:
         raise UserError(_('Nilai BG Belum Diisi'))

      self.no_invoice.bg = 'No BG : ' + str(self.no_bg) +'\n'+'Tgl : ' + str(self.tgl_bg) + '\n' +'Bank : ' +str(self.nama_bank.name)  + '\n' + 'Nilai : '+str(self.nilai_bg)
      self.state = 'done' 

class tbl_acc_bank(models.Model):
    _name = 'tbl_acc_bank'

    name = fields.Char('Name') 


class tbl_acc_norek(models.Model):
    _name = 'tbl_acc_norek'


    name = fields.Char('Name') 