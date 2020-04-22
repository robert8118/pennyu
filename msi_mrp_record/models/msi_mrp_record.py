# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018 Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round



class tbl_menu_record(models.Model):
    _name = "tbl_menu_record"

    def _get_id(self):
        production = self.env['mrp.production'].browse(self._context['active_id'])
        location = production.id
        return location or False

    def _get_product(self):
        production = self.env['mrp.production'].browse(self._context['active_id'])
        product = production.product_id
        return product or False



    mrp_id = fields.Many2one('mrp.production',  string="Mrp Number", default=_get_id, readonly=True)
    user_id = fields.Many2one('res.users', 'Operator', default=lambda self: self._uid, readonly=True)
    product_id = fields.Many2one('product.product', 'Product', default=_get_product, readonly=True)


    wo_id = fields.Many2one('mrp.workorder', string='workorder ID')
    wo_product_id = fields.Many2one('product.product', 'Product')
    target_qty = fields.Float('Target')
    out_good = fields.Float('Good')
    out_no_good = fields.Float('Reject')
    rty = fields.Float(compute='_compute_rty',string='RTY (%)', readonly=True, store=True)


    prf = fields.Float('PRF (%)')
    defect_power = fields.Boolean('Defect Man Power')
    defect_material = fields.Boolean('Defect Material')
    defect_mesin = fields.Boolean('Defect Mesin')
    defect_listrik = fields.Boolean('Defect Listrik')

    cng_awal = fields.Float('CNG Awal')
    cng_akhir = fields.Float('CNH Akhir')
    cng_total = fields.Float('CNG Akhir')

    listrik_awal = fields.Float('Listrik Awal')
    listrik_akhir = fields.Float('Listrik Akhir')
    listrik_total = fields.Float('Listrik Total')

    date_planned_start = fields.Datetime('Date Plan')
    date_start = fields.Datetime('Date Start')
    duration_expected = fields.Float('Duration Expected')
    duration = fields.Float('Duration')


    @api.onchange('wo_id')
    def onchange_wo_id(self):
        if self.wo_id:
            wo = self.env['mrp.workorder'].browse(self.wo_id.id)
            self.wo_product_id = wo.product_id.id
            self.target_qty = wo.qty_production
            self.out_good = wo.qty_produced
            self.date_planned_start = wo.date_planned_start
            self.date_start = wo.date_start
            self.duration_expected = wo.duration_expected
            self.duration = wo.duration


    @api.multi
    @api.depends('out_good','out_no_good','target_qty')
    def _compute_rty(self):
        if not self.target_qty == 0:

          if self.out_no_good == 0:
             self.rty = 100
          else:
             self.rty = (self.out_good / ( self.out_good + self.out_no_good )) * 100

          self.prf = ( ( self.out_good + self.out_no_good ) / self.target_qty ) * 100


    def action_submit(self):
      record_obj = self.env['tbl_menu_record_hasil']
      wo_obj = self.env['mrp.workorder']
      
      self.env.cr.execute('SELECT id FROM tbl_menu_record_hasil WHERE mrp_id = %s AND wo_id = %s ' ,(self.mrp_id.id, self.wo_id.id))
      result12 = self.env.cr.fetchall()
#      raise UserError(_(result12))
      if result12:
         raise UserError(_('Record already submited'))
      else:
         data3 = record_obj.create({
                    'date': self.mrp_id.id,
                    'mrp_id': self.mrp_id.id,
                    'user_id': self.user_id.id,
                    'product_id': self.product_id.id,
                    'wo_id': self.wo_id.id,
                    'wo_product_id': self.wo_product_id.id,
                    'target_qty': self.target_qty,
                    'out_good': self.out_good,
                    'out_no_good': self.out_no_good,
                    'rty': self.rty,
                    'prf': self.prf,
                    'defect_power': self.defect_power,
                    'defect_material': self.defect_material,
                    'defect_mesin': self.defect_mesin,
                    'defect_listrik': self.defect_listrik,
                    'cng_awal': self.cng_awal,
                    'cng_akhir': self.cng_akhir,
                    'cng_total': self.cng_total,
                    'listrik_awal': self.listrik_awal,
                    'listrik_akhir': self.listrik_akhir,
                    'listrik_total': self.listrik_total,

                    'date_planned_start': self.date_planned_start,
                    'date_start': self.date_start,
                    'duration_expected': self.duration_expected,
                    'duration': self.duration,
         })

#         move_s = wo_obj.search([('id', '=', self.wo_id.id)])
#         if move_s:
#            move_s.write({'status_record': 'done'})



class tbl_menu_record_hasil(models.Model):
    _name = "tbl_menu_record_hasil"

    mrp_id = fields.Many2one('mrp.production',  string="Mrp Number", readonly=True)
    user_id = fields.Many2one('res.users', 'Operator', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)

    wo_id = fields.Many2one('mrp.workorder', string='workorder ID', readonly=True)
    wo_product_id = fields.Many2one('product.product', 'Product', readonly=True)
    target_qty = fields.Float('Target', readonly=True)
    out_good = fields.Float('Good', readonly=True)
    out_no_good = fields.Float('Reject', readonly=True)
    rty = fields.Float(string='RTY (%)', readonly=True)


    prf = fields.Float('PRF (%)', readonly=True)
    defect_power = fields.Boolean('Defect Man Power', readonly=True)
    defect_material = fields.Boolean('Defect Material', readonly=True)
    defect_mesin = fields.Boolean('Defect Mesin', readonly=True)
    defect_listrik = fields.Boolean('Defect Listrik', readonly=True)

    cng_awal = fields.Float('CNG Awal', readonly=True)
    cng_akhir = fields.Float('CNH Akhir', readonly=True)
    cng_total = fields.Float('CNG Akhir', readonly=True)

    listrik_awal = fields.Float('Listrik Awal', readonly=True)
    listrik_akhir = fields.Float('Listrik Akhir', readonly=True)
    listrik_total = fields.Float('Listrik Total', readonly=True)

    date_planned_start = fields.Datetime('Date Plan')
    date_start = fields.Datetime('Date Start')
    duration_expected = fields.Float('Duration Expected')
    duration = fields.Float('Duration')


class Msi_workorder(models.Model):
    _inherit = 'mrp.workorder'

    status_record = fields.Char('Status Record', default="draft")

