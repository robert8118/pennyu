# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_msi_collection(models.Model):
    _name = 'tbl_msi_collection'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr', 'Confirm'),
        ('submit', 'Submit'),
        ('print', 'Printed'),

        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    name = fields.Char('Nomor',default='New', readonly=True)
    date = fields.Date('Date')
    collector = fields.Many2one('hr.employee','Collector')
    partner_id = fields.Many2one('res.partner','Customer')
    ket = fields.Char('Keterangan')
    detail_id = fields.One2many('tbl_msi_collection_detail_temp','detail_ids','Detail') 


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('collection') or _('New')

        result = super(tbl_msi_collection, self).create(vals)
        return result

    def action_get_data(self):
        detail_obj = self.env['tbl_msi_collection_detail_temp']

        if not self.partner_id:
           raise UserError(_('Nama Customer Belum Diisi'))

        self.env.cr.execute('SELECT id, date_due, date_invoice, partner_id, residual, journal_id FROM account_invoice WHERE partner_id = %s and state = %s' ,(self.partner_id.id,'open'))
        for row in self.env.cr.fetchall(): 


           self.env.cr.execute('SELECT id FROM account_journal WHERE id = %s and type = %s' ,(row[5],'sale'))
           for row2 in self.env.cr.fetchall():
             
#                 data_line2 = detail_obj.create({
#                    'pay_details': self.id,
#                    'name': row[0],
#                    'partner_id': row[3],
#                    'amount': row[4],
#                 })
                 data_line2 = detail_obj.create({
                    'detail_ids': self.id,
                    'name': row[0],
                    'tgl_inv': row[2],
                    'due_inv': row[1],
                    'partner_id': row[3],
                    'nominal_inv': row[4],
                 })
        self.state = 'appr'

    def action_confirm(self):
        for set in self.detail_id:
            self.env.cr.execute('delete from tbl_msi_collection_detail_temp where to_collect = %s and detail_ids = %s' ,(False,self.id))
        self.state = 'submit' 


    def action_submit(self):
        detail_obj = self.env['tbl_msi_collection_detail']
        for set in self.detail_id:
            set.name.status_penagihan1 = 10

            cari = self.env['tbl_msi_collection_detail'].search([('name','=',set.name.id)])
            if not cari:
                 data_line2 = detail_obj.create({
                    'name': set.name.id,
                    'tgl_inv': set.tgl_inv,
                    'due_inv': set.due_inv,
                    'partner_id': set.partner_id.id,
                    'nominal_inv': set.nominal_inv,
                 })

        self.state = 'print'



class tbl_msi_collection_detail_temp(models.Model):
    _name = 'tbl_msi_collection_detail_temp'

    detail_ids = fields.Many2one('tbl_msi_collection','Detail')
    name = fields.Many2one('account.invoice','Nomer Invoice')
    tgl_inv = fields.Date('Tgl Invoice')
    due_inv = fields.Date('Jatuh Tempo') 
    partner_id = fields.Many2one('res.partner','Customer') 
    nominal_inv = fields.Float('NIlai') 
    status = fields.Many2one('tbl_collection_status','Status')
    ket = fields.Char('Keterangan')
    to_collect = fields.Boolean('to Collect')


class tbl_msi_collection_detail(models.Model):
    _name = 'tbl_msi_collection_detail'

    detail_ids = fields.Many2one('tbl_msi_collection','Detail')
    name = fields.Many2one('account.invoice','Nomer Invoice')
    tgl_inv = fields.Date('Tgl Invoice')
    due_inv = fields.Date('Jatuh Tempo') 
    partner_id = fields.Many2one('res.partner','Customer') 
    nominal_inv = fields.Float('NIlai') 
    status = fields.Many2one('tbl_collection_status','Status')
    ket = fields.Char('Keterangan')
    detail_line = fields.One2many('tbl_msi_collection_detail_line','detail_lines','Detail Status')
    to_collect = fields.Boolean('to Collect')
    state = fields.Selection([
        ('draft', 'Inprogress'),
        ('done', 'Done'),
        ], string='Status Invoice', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


    def action_submit(self):
        self.state = 'done'
 

class tbl_msi_collection_detail_line(models.Model):
    _name = 'tbl_msi_collection_detail_line'

    detail_lines = fields.Many2one('tbl_msi_collection_detail','Detail Status')
    tgl = fields.Date('Tgl')
    collector = fields.Many2one('hr.employee','Collector')
    status = fields.Many2one('tbl_collection_status','Status')
    ket = fields.Char('Keterangan') 




class tbl_collection_status(models.Model):
    _name = 'tbl_collection_status'


    name = fields.Char('Name')
