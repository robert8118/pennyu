# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_msi_acc_mhd(models.Model):
    _name = 'tbl_msi_acc_mhd'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr', 'To Approve'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    name = fields.Char('Nomor',default='New', readonly=True)
    date = fields.Date('Date') 
    partner_id = fields.Many2one('res.partner','Partner')
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    property_account_mhd = fields.Many2one('account.account', string="MHD Account", required=True)
    saldo = fields.Float(compute='_compute_total', string='Total', readonly=True, store=True)
    jumlah_request = fields.Float('Request')

    property_account_intransit = fields.Many2one('account.account', string="Intransit Account", required=True)
    detail_id = fields.One2many('tbl_msi_acc_mhd_detail','detail_ids','Detail')

    @api.multi
    @api.depends('detail_id')
    def _compute_total(self):
        debit=0
        credit=0
        for wo in self:
          for harga in wo.detail_id:
            if harga.to_bill:        
               debit += harga.debit
               credit += harga.credit
          wo.saldo = debit - credit

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ymhd') or _('New')

        result = super(tbl_msi_acc_mhd, self).create(vals)
        return result


    def action_get_data(self):
        detail_obj = self.env['tbl_msi_acc_mhd_detail']
        if self.analytic_id:
           if self.detail_id:
              self.env.cr.execute('delete from tbl_msi_acc_mhd_detail where detail_ids = %s' ,(self.id,))

           self.env.cr.execute('SELECT amount, name, date, id FROM account_analytic_line WHERE account_id = %s and to_bill1 = %s' ,(self.analytic_id.id,0))
           for row in self.env.cr.fetchall(): 
               if row[0] < 0:
                 data_line2 = detail_obj.create({
                    'detail_ids': self.id,
                    'name': row[1],
                    'date': row[2],
                    'debit': row[0]*-1,
                    'analytic_line_id': row[3],
                 })


    def action_submit(self):
      if self.jumlah_request > self.saldo:
         raise UserError(_('Nilai Request harus lebih besar dari total saldo'))
      self.state = 'appr'



    def action_approve(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']


      if not self.partner_id.property_account_mhd:
         raise UserError(_('Account MHD pada partner belum di set'))

      if self.jumlah_request == 0:
         raise UserError(_('Jumlah Request tidak boleh 0'))

      if not self.partner_id.journal_id:
         raise UserError(_('Jurnal MHD pada partner belum di set'))



      data2 = account_move_obj.create({
                    'journal_id': self.partner_id.journal_id.id,
                    'date': fields.Datetime.now(),
                    'ref': self.name,

      })


      data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.partner_id.journal_id.id,
                    'account_id': self.property_account_intransit.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'credit': self.jumlah_request,
      })

      data4 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.partner_id.journal_id.id,
                    'account_id': self.property_account_mhd.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'debit': self.jumlah_request,
                    'analytic_account_id': self.analytic_id.id,
      })
      data2.post()
      for set in self.detail_id:
          set.analytic_line_id.to_bill1 = 1
      self.state = 'done'


class tbl_msi_acc_mhd_detail(models.Model):
    _name = 'tbl_msi_acc_mhd_detail'

    detail_ids = fields.Many2one('tbl_msi_acc_mhdl','Detail')
    to_bill = fields.Boolean('')
    name = fields.Char('Name')
    date = fields.Date('Date')
    debit = fields.Float('Amount') 
    credit = fields.Float('Credit') 
    analytic_line_id = fields.Many2one('account.analytic.line','Analytic Line') 


class msi_account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    to_bill1 = fields.Float('', default=0) 


