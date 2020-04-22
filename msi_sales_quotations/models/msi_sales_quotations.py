# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class msi_sales_quotations(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sepakat', 'Sepakat'),
        ('contract', 'Contract'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    sold_to = fields.Many2one('res.partner','Sold To') 

    delivery_manual = fields.Text('Delivery Manual') 
    nama_ekspedisi = fields.Many2one('res.partner','Nama Ekspedisi') 

    no_aks = fields.Char('ID Paket') 
    no_po = fields.Char('No PO')
    tgl_akhir_kontrak = fields.Date('Tgl Akhir Kontrak') 

#Tree
    invoice_status = fields.Char('Invoice Status') 
    no_delivery_order = fields.Char('No. Delivery Order')
    no_invoice = fields.Char('No. Invoice') 
#/Tree
    note_to_wh = fields.Text('Note Warehouse')
    disc_tambahan = fields.Float('Disc Tambahan')
    disc_tambahan_p = fields.Float('Disc Tambahan Persen')
    sale_ongkir = fields.Float('Biaya Kirim')

    sale_ppn = fields.Float(compute='_compute_sale_ppn', string='PPN', readonly=True, store=True)
    sale_total = fields.Float(compute='_compute_sale_total', string='TOTAL', readonly=True, store=True)


    negosiasi_ids = fields.One2many(
		comodel_name="tbl_msi_negosiasi",
		string="Negosiasi",
		inverse_name="sale_order_id",
		)

    total_harga_barang = fields.Monetary(compute='_compute_total_harga_barang', string='Total harga Barang', readonly=True, store=True)
    nilai_awal_harga_barang = fields.Monetary(compute='_compute_nilai_awal_harga_barang', string='Nilai Awal Harga Barang', readonly=True, store=True)
    total_asuransi = fields.Monetary(compute='_compute_total_asuransi', string='Total Asuransi', readonly=True, store=True)
    total_ongkir = fields.Monetary(compute='_compute_total_ongkir', string='Total Ongkir', readonly=False, store=True)
    total_ongkir_asuransi = fields.Monetary(compute='_compute_total_ongkir_asuransi', string='Total Ongkir + Asuransi', readonly=True, store=True)
    total_transaksi = fields.Monetary(compute='_compute_total_transaksi', string='Total Transaksi', readonly=True, store=True)

    nego_so_id = fields.One2many(
		comodel_name="tbl_msi_nego_so",
		string="Nego SO",
		inverse_name="sale_order_id",
		)

    total_selisih = fields.Monetary(compute='_compute_total_selisih', string='Total Selisih', readonly=True, store=True)
    total_transaksi_setelah_nego = fields.Monetary(compute='_compute_total_transaksi_setelah_nego', string='Total Transaksi Setelah Nego', readonly=True, store=True)

    nego_finansial_id = fields.One2many(
		comodel_name="tbl_msi_nego_finansial",
		string="Nego Finansial",
		inverse_name="sale_order_id",
		)

    ska_id = fields.One2many(
		comodel_name="tbl_msi_ska",
		string="SKA",
		inverse_name="sale_order_id",
		)

    ska_biaya_id = fields.One2many(
		comodel_name="tbl_msi_ska_biaya",
		string="SKA Biaya",
		inverse_name="sale_order_id",
		)

    tgl_sepakat = fields.Datetime('Tgl Sepakat') 
    nilai_bruto = fields.Float(compute='_compute_nilai_bruto', string='Nilai Bruto', readonly=True, store=True)

    discount = fields.Float(compute='_compute_discount', string='Discount', readonly=True, store=True)
    discount_persen = fields.Float(compute='_compute_discount_persen', string='Discount Persen', readonly=True, store=True)

    biaya = fields.Float(compute='_compute_biaya', string='Biaya', readonly=True, store=True)
    biaya_persen = fields.Float(compute='_compute_biaya_persen', string='Biaya Persen', readonly=True, store=True)

    nilai_netto = fields.Float(compute='_compute_nilai_netto', string='Nilai Netto', readonly=True, store=True)
    total_sebelum_ppn = fields.Float(compute='_compute_total_sebelum_ppn', string='Total Sebelum PPN', readonly=True, store=True)
    ppn = fields.Float(compute='_compute_ppn', string='PPN', readonly=True, store=True)
    total_setelah_ppn = fields.Float(compute='_compute_total_setelah_ppn', string='Total Setelah PPN', readonly=True, store=True)

    catatan_negosiasi = fields.Text('Catatan Negosiasi')
    catatan_ska = fields.Text('Catatan SKA')
    total_harga_barang_setelah_nego = fields.Monetary(compute='_compute_total_harga_barang_setelah_nego', string='Total harga Barang', readonly=True, store=True)


    @api.onchange('disc_tambahan_p')
    def onchange_disc_tambahan_p(self):
        if self.disc_tambahan_p:
            self.disc_tambahan = self.amount_untaxed * (self.disc_tambahan_p / 100)

    @api.onchange('disc_tambahan')
    def onchange_disc_tambahan(self):
        if self.disc_tambahan:
            self.disc_tambahan_p = 100 * (self.disc_tambahan / self.amount_untaxed)


    @api.multi
    @api.depends('amount_untaxed','disc_tambahan')
    def _compute_sale_ppn(self):
        for wo in self:  
            wo.sale_ppn = (wo.amount_untaxed - wo.disc_tambahan) / 10

    @api.multi
    @api.depends('amount_untaxed','disc_tambahan','sale_ongkir')
    def _compute_sale_total(self):
        for wo in self: 
            wo.sale_total = (wo.amount_untaxed - wo.disc_tambahan) + wo.sale_ppn + wo.sale_ongkir


    @api.multi
    @api.depends('negosiasi_ids')
    def _compute_total_harga_barang(self):
        for wo in self:
            for harga in wo.negosiasi_ids:        
               wo.total_harga_barang += harga.total

    @api.multi
    @api.depends('negosiasi_ids')
    def _compute_total_harga_barang_setelah_nego(self):
        for wo in self:
            for harga in wo.negosiasi_ids:        
               wo.total_harga_barang_setelah_nego += harga.total_setelah_nego

    @api.multi
    @api.depends('total_harga_barang')
    def _compute_nilai_awal_harga_barang(self):
        for wo in self:
            wo.nilai_awal_harga_barang = wo.total_harga_barang/1.1

    @api.multi
    @api.depends('negosiasi_ids')
    def _compute_total_asuransi(self):
        for wo in self:
            for harga in wo.negosiasi_ids:        
               wo.total_asuransi += harga.asuransi_value

    @api.multi
    @api.depends('negosiasi_ids')
    def _compute_total_ongkir(self):
        for wo in self:
            for harga in wo.negosiasi_ids:        
               wo.total_ongkir += harga.ongkir2

    @api.multi
    @api.depends('total_ongkir' , 'total_asuransi')
    def _compute_total_ongkir_asuransi(self):
        for wo in self:
            wo.total_ongkir_asuransi = wo.total_ongkir + wo.total_asuransi

    @api.multi
    @api.depends('negosiasi_ids')
    def _compute_total_transaksi(self):
        for wo in self:
            for harga in wo.negosiasi_ids:        
               wo.total_transaksi += harga.total_transaksi

    @api.multi
    @api.depends('nego_so_id')
    def _compute_total_selisih(self):
        for wo in self:
            for harga in wo.nego_so_id:        
               wo.total_selisih += harga.selisih

    @api.multi
    @api.depends('nego_so_id','total_harga_barang_setelah_nego')
    def _compute_total_transaksi_setelah_nego(self):
        total_nego=0
        for wo in self:
            for harga in wo.nego_so_id:
             if harga.tipe_transaksi == 'mf':
               total_nego += harga.nilai_yg_disetujui        
            wo.total_transaksi_setelah_nego = wo.total_harga_barang_setelah_nego + total_nego

    @api.multi
    @api.depends('ska_id')
    def _compute_nilai_bruto(self):
        for wo in self:
            for harga in wo.ska_id:        
               wo.nilai_bruto += harga.harga_bruto

    @api.multi
    @api.depends('ska_id')
    def _compute_discount(self):
        for wo in self:
            for harga in wo.ska_id:        
               wo.discount += harga.diskon

    @api.multi
    @api.depends('discount', 'total_sebelum_ppn')
    def _compute_discount_persen(self):
        for wo in self:
            if wo.total_sebelum_ppn == 0:
               wo.discount_persen == 0
            else:
              if wo.total_sebelum_ppn < 0:
                 wo.discount_persen = 0
              else:
                 wo.discount_persen = (wo.discount / wo.nilai_bruto)*100


    @api.multi
    @api.depends('ska_biaya_id')
    def _compute_biaya(self):
        for wo in self:
            for harga in wo.ska_biaya_id:        
               wo.biaya += harga.harga

    @api.multi
    @api.depends('biaya', 'total_sebelum_ppn')
    def _compute_biaya_persen(self):
        for wo in self:
            if wo.total_sebelum_ppn == 0:
               wo.biaya_persen == 0
            else:
              if wo.total_sebelum_ppn < 0:
                 wo.biaya_persen = 0
              else:
                 wo.biaya_persen = (wo.biaya / wo.nilai_bruto)*100


    @api.multi
    @api.depends('nilai_bruto', 'discount', 'biaya')
    def _compute_nilai_netto(self):
        for wo in self:
            wo.nilai_netto = wo.nilai_bruto - wo.discount - wo.biaya

    @api.multi
    @api.depends('ska_id')
    def _compute_total_sebelum_ppn(self):
        for wo in self:
            for harga in wo.ska_id:        
               wo.total_sebelum_ppn += harga.harga_dpp

    @api.multi
    @api.depends('ska_id')
    def _compute_ppn(self):
        for wo in self:
            for harga in wo.ska_id:        
               wo.ppn += harga.ppn2

    @api.multi
    @api.depends('total_sebelum_ppn', 'ppn')
    def _compute_total_setelah_ppn(self):
        for wo in self:
            wo.total_setelah_ppn = wo.total_sebelum_ppn + wo.ppn



    def action_sepakat(self):
      self.state = 'sepakat'

    def action_contract(self):
      self.state = 'contract'



class tbl_msi_negosiasi(models.Model):
    _name = 'tbl_msi_negosiasi'

    product = fields.Many2one('product.product','Product')
    berat_unit = fields.Float('Berat/Unit (KG)')
    ongkir = fields.Float('Ongkir')
    harga_satuan = fields.Float('Harga Satuan')
    qty = fields.Float('Qty', default=1)

    total = fields.Float(compute='_compute_total', string='Total', readonly=True, store=True)

    asuransi_persen = fields.Float('Asuransi (%)', default=0.25)
    asuransi_value = fields.Float(compute='_compute_asuransi', string='Asuransi Value', readonly=True, store=True)

    total_berat_kg = fields.Float(compute='_compute_berat_kg', string='Total Berat (Kg)', readonly=True, store=True)
    ongkir2 = fields.Float(compute='_compute_ongkir2', string='Total Ongkir', readonly=True, store=True)
    total_transaksi = fields.Float(compute='_compute_total_transaksi', string='Total Transaksi', readonly=True, store=True)
    ongkir_nego = fields.Float('Ongkir Nego')
    harga_satuan_setelah_nego = fields.Float(string='Harga Satuan Setelah Nego')
    dpp = fields.Float(compute='_compute_dpp', string='DPP', readonly=True, store=True)
    ppn = fields.Float(compute='_compute_ppn', string='PPN', readonly=True, store=True)
    total_setelah_nego = fields.Float(compute='_compute_total_setelah_nego', string='Total', readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order','Sale Order')

    @api.onchange('product')
    def onchange_product(self):
        if self.product:
            self.berat_unit = self.product.weight
            self.harga_satuan = self.product.standard_price

    @api.onchange('ongkir_nego')
    def onchange_ongkir_nego(self):
        if self.ongkir_nego:
            self.harga_satuan_setelah_nego = (self.ongkir_nego + self.total)/self.qty

    @api.onchange('total')
    def onchange_total(self):
        if self.total:
            self.harga_satuan_setelah_nego = (self.ongkir_nego + self.total)/self.qty

    @api.onchange('qty')
    def onchange_qty(self):
        if self.qty:
            self.harga_satuan_setelah_nego = (self.ongkir_nego + self.total)/self.qty


    @api.multi
    @api.depends('qty', 'harga_satuan')
    def _compute_total(self):
        for wo in self:
            wo.total = wo.harga_satuan * wo.qty

    @api.multi
    @api.depends('qty', 'harga_satuan','harga_satuan_setelah_nego')
    def _compute_total_setelah_nego(self):
        for wo in self:
            wo.total_setelah_nego = wo.harga_satuan_setelah_nego * wo.qty


    @api.multi
    @api.depends('total', 'asuransi_persen')
    def _compute_asuransi(self):
        for wo in self:
            if wo.asuransi_persen == 0:
               wo.asuransi_value = 0
            else:
              if wo.asuransi_persen < 0:
                 wo.asuransi_value = 0
              else:
                 wo.asuransi_value = wo.total * (wo.asuransi_persen/100)

    @api.multi
    @api.depends('qty', 'berat_unit')
    def _compute_berat_kg(self):
        for wo in self:
            wo.total_berat_kg = math.ceil(wo.berat_unit * wo.qty)

    @api.multi
    @api.depends('ongkir', 'total_berat_kg')
    def _compute_ongkir2(self):
        for wo in self:
            wo.ongkir2 = wo.ongkir * wo.total_berat_kg

    @api.multi
    @api.depends('total', 'asuransi_value', 'ongkir2')
    def _compute_total_transaksi(self):
        for wo in self:
            wo.total_transaksi = wo.total + wo.asuransi_value + wo.ongkir2

    @api.multi
    @api.depends('ongkir_nego', 'total', 'qty')
    def _compute_harga_satuan_setelah_nego(self):
        for wo in self:
            wo.harga_satuan_setelah_nego = (wo.ongkir_nego + wo.total)/wo.qty

    @api.multi
    @api.depends('harga_satuan_setelah_nego')
    def _compute_dpp(self):
        for wo in self:
            wo.dpp = wo.harga_satuan_setelah_nego/1.1

    @api.multi
    @api.depends('dpp')
    def _compute_ppn(self):
        for wo in self:
            wo.ppn = wo.dpp/10

    def add_to_sq(self):
      sale_line_obj = self.env['sale.order.line']
      data3 = sale_line_obj.create({
                    'order_id': self.sale_order_id.id,
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'price_unit': self.dpp,
                    'product_uom_qty': self.qty,
                    'product_uom ': self.product.uom_id.id
      })



class tbl_msi_nego_so(models.Model):
    _name = 'tbl_msi_nego_so'

    jenis_pengajuan = fields.Many2one('tbl_jenis_pengajuan','Jenis Pengajuan')
    tipe_transaksi = fields.Selection([ ('df','DF'),('mf','MF')],'Tipe', default='df')
    nilai_awal = fields.Float('Nilai Awal')
    nilai_pengajuan = fields.Float('Nilai Pengajuan')
    selisih = fields.Float(compute='_compute_selisih', string='Selisih', readonly=True, store=True)
    nilai_yg_disetujui = fields.Float('Nilai yang Disetujui')
    keterangan = fields.Char('Keterangan')

    sale_order_id = fields.Many2one('sale.order','Sale Order')

    @api.multi
    @api.depends('nilai_awal', 'nilai_pengajuan')
    def _compute_selisih(self):
        for wo in self:
            wo.selisih = wo.nilai_awal - wo.nilai_pengajuan

class tbl_msi_nego_finansial(models.Model):
    _name = 'tbl_msi_nego_finansial'

    product = fields.Many2one('tbl_msi_product_ska' , 'Jenis Pengajuan')
    nilai_awal = fields.Float('Nilai Awal')
    nilai_pengajuan = fields.Float(compute='_compute_nilai_pengajuan', string='Nilai Pengajuan', readonly=True, store=True)
    selisih = fields.Float(compute='_compute_selisih', string='Selisih', readonly=True, store=True)
    nilai_yg_disetujui = fields.Float(compute='_compute_nilai_yg_disetujui', string='Nilai yang Disetujui', readonly=True, store=True)
    nilai_akhir = fields.Float('Nilai Akhir')
    persen = fields.Float('%')
    qty = fields.Float('Qty', default=1)
    pajak = fields.Selection([ ('include','Include PPN'),('exclude','Exclude PPN')],'Pajak', default='exclude')
    keterangan = fields.Char('Keterangan')
    analytic_id = fields.Many2one('account.analytic.account', required=True, string='Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    sale_order_id = fields.Many2one('sale.order','Sale Order')

    @api.multi
    @api.depends('nilai_awal', 'nilai_akhir')
    def _compute_selisih(self):
        for wo in self:
            wo.selisih = wo.nilai_awal - wo.nilai_akhir

    @api.multi
    @api.depends('selisih', 'persen')
    def _compute_nilai_pengajuan(self):
        for wo in self:
            wo.nilai_pengajuan = wo.selisih * (wo.persen/100)

    @api.multi
    @api.depends('nilai_pengajuan')
    def _compute_nilai_yg_disetujui(self):
        for wo in self:
            wo.nilai_yg_disetujui = wo.nilai_pengajuan


    def submit_to_acc_nego(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']


      if not self.sale_order_id.partner_id.property_account_mhd:
         raise UserError(_('Account MHD pada partner belum di set'))

      if not self.sale_order_id.partner_id.journal_id:
         raise UserError(_('Jurnal MHD pada partner belum di set'))

      if not  self.product.account_id:
         raise UserError(_('Account pada product ska atau negoisasi belum di set'))

      data2 = account_move_obj.create({
                    'journal_id': self.sale_order_id.partner_id.journal_id.id,
                    'date': fields.Datetime.now(),
                    'ref': 'ACCRUE ' + str(self.product.name) + ' '+ str(self.sale_order_id.partner_id.name) + ' ' +self.sale_order_id.name,

      })


      data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': 'ACCRUE ' + str(self.product.name) + ' '+ str(self.sale_order_id.partner_id.name) + ' ' +self.sale_order_id.name,
                    'partner_id': self.sale_order_id.partner_id.id,
                    'date': fields.Datetime.now(),
                    'journal_id': self.sale_order_id.partner_id.journal_id.id,
                    'account_id': self.product.account_id.id,
                    'move_id': data2.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': fields.Datetime.now(),
                    'debit': self.nilai_yg_disetujui,
                    'analytic_account_id': self.analytic_id.id,

      })

      data4 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': 'ACCRUE ' + str(self.product.name) + ' '+ str(self.sale_order_id.partner_id.name) + ' ' +self.sale_order_id.name,
                    'partner_id': self.sale_order_id.partner_id.id,
                    'date': fields.Datetime.now(),
                    'journal_id': self.sale_order_id.partner_id.journal_id.id,
                    'account_id': self.product.account_mhd_id.id,
                    'move_id': data2.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': fields.Datetime.now(),
                    'credit': self.nilai_yg_disetujui,


      })
      data2.post()
      self.status_acc = True

class tbl_jenis_pengajuan(models.Model):
    _name = 'tbl_jenis_pengajuan'

    name = fields.Char('Name')

class tbl_msi_ska(models.Model):
    _name = 'tbl_msi_ska'

    product = fields.Many2one('product.product','Product')
    harga_satuan = fields.Float('Harga Satuan')
    qty = fields.Float('Qty', default=1)
    harga_bruto = fields.Float(compute='_compute_harga_bruto', string='Harga Bruto', readonly=True, store=True)
    harga_netto = fields.Float('Harga Netto')
    diskon = fields.Float(compute='_compute_diskon', string='Diskon', readonly=True, store=True)
    ppn = fields.Selection([ ('include','Include PPN'),('exclude','Exclude PPN')],'PPN', default='include')
    ppn2 = fields.Float(compute='_compute_ppn2', string='PPN', readonly=True, store=True)
    harga_dpp = fields.Float(compute='_compute_dpp', string='DPP', readonly=True, store=True)

    sale_order_id = fields.Many2one('sale.order','Sale Order')

    @api.onchange('product')
    def onchange_product(self):
        if self.product:
            self.harga_satuan = self.product.standard_price

    @api.multi
    @api.depends('qty', 'harga_satuan')
    def _compute_harga_bruto(self):
        for wo in self:
            wo.harga_bruto = wo.harga_satuan * wo.qty

    @api.multi
    @api.depends('harga_bruto', 'harga_netto','ppn')
    def _compute_diskon(self):
        for wo in self:
            if wo.ppn == 'include':
               wo.diskon = (wo.harga_bruto - wo.harga_netto)+((wo.harga_netto/1.1)/10)


            else:
               wo.diskon = wo.harga_bruto - wo.harga_netto


    @api.multi
    @api.depends('harga_netto','ppn')
    def _compute_ppn2(self):
        for wo in self:
            if wo.ppn == 'include':
               wo.ppn2 = (wo.harga_netto/1.1)/10
            else:
               wo.ppn2 = wo.harga_netto/10

    @api.multi
    @api.depends('harga_netto','ppn')
    def _compute_dpp(self):
        for wo in self:
            if wo.ppn == 'include':
               wo.harga_dpp = wo.harga_netto/1.1
            else:
               wo.harga_dpp = wo.harga_netto

    def transfer_to_sq(self):
      sale_line_obj = self.env['sale.order.line']


      data3 = sale_line_obj.create({
                    'order_id': self.sale_order_id.id,
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'price_unit': self.harga_netto,
                    'product_uom_qty': self.qty,
                    'product_uom ': self.product.uom_id.id


      })

class tbl_msi_ska_biaya(models.Model):
    _name = 'tbl_msi_ska_biaya'

    product = fields.Many2one('tbl_msi_product_ska' , 'Product')
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    harga_satuan = fields.Float('Harga Satuan', required=True)
    qty = fields.Float('Qty', default=1)
    harga = fields.Float(compute='_compute_harga', string='Harga', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)

    sale_order_id = fields.Many2one('sale.order','Sale Order')
    status_acc = fields.Boolean('Status Acc')


    @api.multi
    @api.depends('qty', 'harga_satuan')
    def _compute_harga(self):
        for wo in self:
            wo.harga = wo.harga_satuan * wo.qty



    def submit_to_acc_ska(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']


      if not self.sale_order_id.partner_id.property_account_mhd:
         raise UserError(_('Account MHD pada partner belum di set'))

      if not self.sale_order_id.partner_id.journal_id:
         raise UserError(_('Jurnal MHD pada partner belum di set'))

      if not  self.product.account_id:
         raise UserError(_('Account pada product ska atau negoisasi belum di set'))

      data2 = account_move_obj.create({
                    'journal_id': self.sale_order_id.partner_id.journal_id.id,
                    'date': fields.Datetime.now(),
                    'ref': 'ACCRUE ' + str(self.product.name) + ' '+ str(self.sale_order_id.partner_id.name) + ' ' +self.sale_order_id.name,

      })


      data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': 'ACCRUE ' + str(self.product.name) + ' '+ str(self.sale_order_id.partner_id.name) + ' ' +self.sale_order_id.name,
                    'partner_id': self.sale_order_id.partner_id.id,
                    'date': fields.Datetime.now(),
                    'journal_id': self.sale_order_id.partner_id.journal_id.id,
                    'account_id': self.product.account_id.id,
                    'move_id': data2.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': fields.Datetime.now(),
                    'debit': self.harga,
                    'analytic_account_id': self.analytic_id.id,

      })

      data4 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': 'ACCRUE ' + str(self.product.name) + ' '+ str(self.sale_order_id.partner_id.name) + ' ' +self.sale_order_id.name,
                    'partner_id': self.sale_order_id.partner_id.id,
                    'date': fields.Datetime.now(),
                    'journal_id': self.sale_order_id.partner_id.journal_id.id,
                    'account_id': self.product.account_mhd_id.id,
                    'move_id': data2.id,
                    'currency_id': self.currency_id.id,
                    'date_maturity': fields.Datetime.now(),
                    'credit': self.harga,


      })
      data2.post()
      self.status_acc = True




class tbl_msi_product_ska(models.Model):
    _name = 'tbl_msi_product_ska'

    name = fields.Char('Product')
    account_id = fields.Many2one('account.account', string='Account',
        required=True,
        help="The income or expense account related to the selected product.")
    account_mhd_id = fields.Many2one('account.account', string='Account MHD',
        required=True,
        help="The income or expense account related to the selected product.")



