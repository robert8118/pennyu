# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_msi_acc_settlement(models.Model):
    _name = 'tbl_msi_acc_settlement'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr', 'Approve Advanced'),
        ('submit2', 'Submit Settlement'),
        ('appr2', 'Approve Settlement'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    name = fields.Char('Nomor',default='New', readonly=True)
    date = fields.Date('Date') 
    employee_id = fields.Many2one('hr.employee','Employee')
    saldo = fields.Float(compute='_compute_total', string='Perkiraan Biaya', readonly=True, store=True)
    settlement = fields.Float(compute='_compute_settlement', string='Total Settlement', readonly=True, store=True)
    selisih = fields.Float(compute='_compute_selisih', string='Selisih', readonly=True, store=True)
    property_account_uang_muka = fields.Many2one('account.account', string="Advanced Account", required=True)

    property_account_intransit = fields.Many2one('account.account', string="Intransit Account Payable", required=True)
    property_account_intransit_recv = fields.Many2one('account.account', string="Intransit Account Receivable", required=True)
    journal_id = fields.Many2one('account.journal', string='Journal Advanced')

    detail_advanced_id = fields.One2many('tbl_msi_acc_settlement_advanced','detail_advanced_ids','Detail Advanced')
    detail_settlement_id = fields.One2many('tbl_msi_acc_settlement_settlement','detail_settlement_ids','Detail Settlement')


    @api.multi
    @api.depends('detail_advanced_id')
    def _compute_total(self):
        debit=0
        credit=0
        for wo in self:
            for harga in wo.detail_advanced_id:        
               debit += harga.amount
            wo.saldo = debit

    @api.multi
    @api.depends('detail_settlement_id')
    def _compute_settlement(self):
        debit=0
        credit=0
        for wo in self:
            for harga in wo.detail_settlement_id:        
               debit += harga.amount
            wo.settlement = debit


    @api.multi
    @api.depends('saldo','settlement')
    def _compute_selisih(self):
        debit=0
        credit=0
        for wo in self:
            for harga in wo.detail_settlement_id:        
               debit = wo.saldo - wo.settlement
            wo.selisih = debit


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('acc_settlement') or _('New')

        result = super(tbl_msi_acc_settlement, self).create(vals)
        return result




    def action_submit(self):
#      if self.selisih < 0:
#         raise UserError(_('Nilai Selisih harus > 0'))
      self.state = 'appr'



    def action_approve1(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']


      if not self.property_account_uang_muka:
         raise UserError(_('Account Advanced belum di set'))

      if not self.property_account_intransit:
         raise UserError(_('Account Intransit belum di set'))

      if not self.journal_id:
         raise UserError(_('Advanced Journal belum di set'))



      data2 = account_move_obj.create({
                    'journal_id': self.journal_id.id,
                    'date': fields.Datetime.now(),
                    'ref': self.name,

      })


      data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.journal_id.id,
                    'account_id': self.property_account_intransit.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'credit': self.saldo,
      })

      data4 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.journal_id.id,
                    'account_id': self.property_account_uang_muka.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'debit': self.saldo,

      })
      data2.post()
      self.state = 'submit2'

    def action_submit2(self):
#      if self.selisih != 0:
#         raise UserError(_('Nilai Selisih harus = 0'))
      self.state = 'appr2'

    def action_approve2(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']


      if not self.property_account_uang_muka:
         raise UserError(_('Account Advanced belum di set'))

      if not self.property_account_intransit:
         raise UserError(_('Account Intransit belum di set'))

      if not self.journal_id:
         raise UserError(_('Advanced Journal belum di set'))



      data2 = account_move_obj.create({
                    'journal_id': self.journal_id.id,
                    'date': fields.Datetime.now(),
                    'ref': self.name,

      })

      data4 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.journal_id.id,
                    'account_id': self.property_account_uang_muka.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'credit': self.saldo,

      })

      if self.selisih < 0:

         data100 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.journal_id.id,
                    'account_id': self.property_account_intransit.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'credit': self.selisih*-1,

      })

      if self.selisih > 0:

         data101 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': fields.Datetime.now(),
                    'journal_id': self.journal_id.id,
                    'account_id': self.property_account_intransit_recv.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'debit': self.selisih,

      })
          

      for line in self.detail_settlement_id:
          data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': str(self.name) + ' ' + str(line.name),
                    'date': fields.Datetime.now(),
                    'journal_id': self.journal_id.id,
                    'account_id': line.property_account_expense.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Datetime.now(),
                    'debit': line.amount,
          })


      data2.post()
      self.state = 'done'


class tbl_msi_acc_settlement_advanced(models.Model):
    _name = 'tbl_msi_acc_settlement_advanced'

    detail_advanced_ids = fields.Many2one('tbl_msi_acc_settlement','Detail')
    name = fields.Char('Label')
    amount = fields.Float('Amount') 


class tbl_msi_acc_settlement_settlement(models.Model):
    _name = 'tbl_msi_acc_settlement_settlement'

    detail_settlement_ids = fields.Many2one('tbl_msi_acc_settlement','Detail')
    name = fields.Char('Label')
    amount = fields.Float('Amount') 
    property_account_expense = fields.Many2one('account.account', string="Expense Account", required=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)




class msi2_invoice(models.Model):
    _inherit = 'account.invoice'

    nama_bg = fields.Char('BG')
