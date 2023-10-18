# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
            
class FpInvoiceExport(models.TransientModel):
    _name = 'fp.invoice.export'
    _inherit = 'fp.invoice.export'
        
    def _get_header_fk(self):
        return ['FK',
                'KD_JENIS_TRANSAKSI',
                'FG_PENGGANTI',
                'NOMOR_FAKTUR',
                'MASA_PAJAK',
                'TAHUN_PAJAK',
                'TANGGAL_FAKTUR',
                'NPWP',
                'NAMA',
                'ALAMAT_LENGKAP',
                'JUMLAH_DPP',
                'JUMLAH_PPN',
                'JUMLAH_PPNBM',
                'ID_KETERANGAN_TAMBAHAN',
                'FG_UANG_MUKA',
                'UANG_MUKA_DPP',
                'UANG_MUKA_PPN',
                'UANG_MUKA_PPNBM',
                'REFERENSI',
                'KODE_DOKUMEN_PENDUKUNG',
                'NIK']
    
    def _get_header_fapr(self, headers):
        fapr_ids = {
            'FK': 'FAPR',
            'KD_JENIS_TRANSAKSI': 'NPWP',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'JALAN',
            'MASA_PAJAK': 'BLOK',
            'TAHUN_PAJAK': 'NOMOR',
            'TANGGAL_FAKTUR': 'RT',
            'NPWP': 'RW',
            'NAMA': 'KECAMATAN',
            'ALAMAT_LENGKAP': 'KELURAHAN',
            'JUMLAH_DPP': 'KABUPATEN',
            'JUMLAH_PPN': 'PROPINSI',
            'JUMLAH_PPNBM': 'KODE_POS',
            'ID_KETERANGAN_TAMBAHAN': 'NOMOR_TELEPON',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': '',
            'KODE_DOKUMEN_PENDUKUNG': '',
            'NIK': ''
        }
        rows = [fapr_ids[l] for l in headers]
        return rows
        
    def _get_header_lt(self, headers):
        lt_ids = {
            'FK': 'LT',
            'KD_JENIS_TRANSAKSI': 'NPWP',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'JALAN',
            'MASA_PAJAK': 'BLOK',
            'TAHUN_PAJAK': 'NOMOR',
            'TANGGAL_FAKTUR': 'RT',
            'NPWP': 'RW',
            'NAMA': 'KECAMATAN',
            'ALAMAT_LENGKAP': 'KELURAHAN',
            'JUMLAH_DPP': 'KABUPATEN',
            'JUMLAH_PPN': 'PROPINSI',
            'JUMLAH_PPNBM': 'KODE_POS',
            'ID_KETERANGAN_TAMBAHAN': 'NOMOR_TELEPON',
            'FG_UANG_MUKA': 'EMAIL',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': '',
            'KODE_DOKUMEN_PENDUKUNG': '',
            'NIK': ''
        }
        rows = [lt_ids[l] for l in headers]
        return rows
    
    def _get_header_of(self, headers):
        of_ids = {
            'FK': 'OF',
            'KD_JENIS_TRANSAKSI': 'KODE_OBJEK',
            'FG_PENGGANTI': 'NAMA',
            'NOMOR_FAKTUR': 'HARGA_SATUAN',
            'MASA_PAJAK': 'JUMLAH_BARANG',
            'TAHUN_PAJAK': 'HARGA_TOTAL',
            'TANGGAL_FAKTUR': 'DISKON',
            'NPWP': 'DPP',
            'NAMA': 'PPN',
            'ALAMAT_LENGKAP': 'TARIF_PPNBM',
            'JUMLAH_DPP': 'PPNBM',
            'JUMLAH_PPN': '',
            'JUMLAH_PPNBM': '',
            'ID_KETERANGAN_TAMBAHAN': '',
            'FG_UANG_MUKA': '',
            'UANG_MUKA_DPP': '',
            'UANG_MUKA_PPN': '',
            'UANG_MUKA_PPNBM': '',
            'REFERENSI': '',
            'KODE_DOKUMEN_PENDUKUNG': '',
            'NIK': ''
        }
        rows = [of_ids[o] for o in headers]
        return rows
    
    def _get_invoice_line(self, headers):
        context = dict(self._context or {})
        Invoice = self.env['account.invoice']
        invoices = Invoice.browse(context.get('active_ids'))
        rows = []
        for inv in invoices:
            total_dpp = sum(self._amount_currency_line(line.price_subtotal, line) for line in inv.invoice_line_ids) or 0
            total_ppn = sum(self._amount_currency_line(line.price_tax, line) for line in inv.invoice_line_ids) or 0
            tot_line_dpp = sum(int(round(self._amount_currency_line(line.price_subtotal, line),0)) for line in inv.invoice_line_ids) or 0
            tot_line_ppn = sum(int(round(self._amount_currency_line(line.price_tax, line),0)) for line in inv.invoice_line_ids) or 0
            max_line_id = max(line for line in inv.invoice_line_ids if line.invoice_line_tax_ids) or 0
            
            if inv.state in ('draft','cancel'):
                raise UserError(_('Cannot export draft/cancel Invoice! %s' % inv.origin))
            if not inv.amount_tax:
                raise UserError(_('Make sure select invoice which has taxes!'))
            
            if context.get('default_type') in ('out_invoice','out_refund'):
                type = 'Keluaran'
                itype = 'Masukan'
            elif context.get('default_type') in ('in_invoice','in_refund'):
                type = 'Masukan'
                itype = 'Keluaran'
            if context.get('default_type') != inv.type:
                raise UserError(_('Cannot export FP %s Invoice %s as it on FP %s.!' % (itype, inv.number, type)))
            
            amount_untaxed = int(round(total_dpp,0))
            amount_tax = int(round(total_ppn,0))
            residual_dpp = amount_untaxed - tot_line_dpp
            residual_ppn = amount_tax - tot_line_ppn
            fapr_ids = {}
            if context.get('default_type') in ('out_invoice','out_refund'):
                inv_ids = {
                    'FK': 'FK',
                    'KD_JENIS_TRANSAKSI': '01',
                    'FG_PENGGANTI': '0',
                    'NOMOR_FAKTUR': inv.nomor_faktur_id and inv.nomor_faktur_id.number or '',
                    'MASA_PAJAK': int(time.strftime('%m', time.strptime(str(inv.date_invoice),'%Y-%m-%d'))),
                    'TAHUN_PAJAK': time.strftime('%Y', time.strptime(str(inv.date_invoice),'%Y-%m-%d')),
                    'TANGGAL_FAKTUR': time.strftime('%d/%m/%Y', time.strptime(str(inv.date_invoice),'%Y-%m-%d')),
                    'NPWP': inv.npwp_efaktur or '000000000000000',
                    'NAMA': inv.partner_id.name or '',
                    'ALAMAT_LENGKAP': inv.partner_id._get_street_npwp() or '',
                    'JUMLAH_DPP': amount_untaxed or 0,
                    'JUMLAH_PPN': amount_tax or 0,
                    'JUMLAH_PPNBM': 0,
                    'ID_KETERANGAN_TAMBAHAN': '',
                    'FG_UANG_MUKA': 0,
                    'UANG_MUKA_DPP': 0,
                    'UANG_MUKA_PPN': 0,
                    'UANG_MUKA_PPNBM': 0,
                    'REFERENSI': inv.number or inv.origin or '',
                    'KODE_DOKUMEN_PENDUKUNG': '',
                    'NIK': inv.partner_id.ktp or inv.partner_id.no_ktp or ''
                }
            elif context.get('default_type') in ('in_invoice','in_refund'):
                inv_ids = {
                    'FM': 'FM',
                    'KD_JENIS_TRANSAKSI': '01',
                    'FG_PENGGANTI': '0',
                    'NOMOR_FAKTUR': inv.nomor_faktur_id and inv.nomor_faktur_id.number or '',
                    'MASA_PAJAK': int(time.strftime('%m', time.strptime(str(inv.date_invoice),'%Y-%m-%d'))),
                    'TAHUN_PAJAK': time.strftime('%Y', time.strptime(str(inv.date_invoice),'%Y-%m-%d')),
                    'TANGGAL_FAKTUR': time.strftime('%d/%m/%Y', time.strptime(str(inv.date_invoice),'%Y-%m-%d')),
                    'NPWP': inv.npwp_efaktur or '000000000000000',
                    'NAMA': inv.partner_id._get_name_npwp() or '',
                    'ALAMAT_LENGKAP': inv.partner_id._get_street_npwp() or '',
                    'JUMLAH_DPP': amount_untaxed or 0,
                    'JUMLAH_PPN': amount_tax or 0,
                    'JUMLAH_PPNBM': 0,
                    'IS_CREDITABLE': '1',
                }
            row = [inv_ids[i] for i in headers]
            rows.append(list(row))
            if fapr_ids:
                row_fapr = [fapr_ids[i] for i in headers]
                rows.append(list(row_fapr))
            
            if context.get('default_type') in ('out_invoice','out_refund'):
                for line in inv.invoice_line_ids:
                    if line.invoice_line_tax_ids:
                        line_dpp = int(round(self._amount_currency_line(line.price_subtotal, line),0))
                        line_ppn = line.invoice_line_tax_ids and int(round(self._amount_currency_line(line.price_tax, line),0))
                        
                        if inv.company_id.discount_efaktur_display == 'no':
                            HARGA_SATUAN = int(self._amount_currency_line(line.price_subtotal/line.quantity, line)) or '0'
                            JUMLAH_BARANG = line.quantity or 1
                            HARGA_TOTAL = int(self._amount_currency_line(line.price_subtotal, line)) or '0'
                            DISKON = '0'
                        else:
                            HARGA_SATUAN = int(round(self._amount_currency_line(line.price_unit_undiscount_untaxed, line),0)) or '0'
                            JUMLAH_BARANG = line.quantity or 1
                            HARGA_TOTAL = int(self._amount_currency_line(line.price_undiscount_untaxed, line)) or '0'
                            DISKON = int(line.price_discount_untaxed) or '0'
                        DPP = max_line_id == line and line_dpp + residual_dpp or line_dpp or '0'
                        PPN = max_line_id == line and line_ppn + residual_ppn or line_ppn or '0'
                        line_ids = {
                            'FK': 'OF',
                            'KD_JENIS_TRANSAKSI': line.product_id.default_code or '',
                            'FG_PENGGANTI': line.product_id.name or '',
                            'NOMOR_FAKTUR': HARGA_SATUAN,
                            'MASA_PAJAK': JUMLAH_BARANG,
                            'TAHUN_PAJAK': HARGA_TOTAL,
                            'TANGGAL_FAKTUR': DISKON,
                            'NPWP': DPP,
                            'NAMA': PPN,
                            'ALAMAT_LENGKAP': '0',
                            'JUMLAH_DPP': '0',
                            'JUMLAH_PPN': '',
                            'JUMLAH_PPNBM': '',
                            'ID_KETERANGAN_TAMBAHAN': '',
                            'FG_UANG_MUKA': '',
                            'UANG_MUKA_DPP': '',
                            'UANG_MUKA_PPN': '',
                            'UANG_MUKA_PPNBM': '',
                            'REFERENSI': '',
                            'KODE_DOKUMEN_PENDUKUNG': '',
                            'NIK': ''
                        }
                        row = [line_ids[l] for l in headers]
                        rows.append(list(row))
        return rows
