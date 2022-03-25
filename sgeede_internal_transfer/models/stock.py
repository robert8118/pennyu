from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from odoo import fields, models
#from odoo.osv import fields, osv
from odoo.tools import float_compare
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import SUPERUSER_ID, api
import odoo.addons.decimal_precision as dp
#from odoo.addons.procurement import procurement
import logging

_logger = logging.getLogger(__name__)

class stock_picking(models.Model):
	_inherit = "stock.picking"

	@api.multi
	def do_internal_transfer_details(self):
		context = dict(self._context or {})

		picking = [picking]

		context.update({
			'active_model': self._name,
			'active_ids': picking,
			'active_id': len(picking) and picking[0] or False
			})

		# created_id = self.env['stock.transfer_details'].with_context(context).create({'picking_id': len(picking) and picking[0] or False})
		# self.env['stock.transfer_details'].do_detailed_transfer(created_id)

		return True

	transfer_id = fields.Many2one('stock.internal.transfer', 'Transfer')

class stock_move(models.Model):
	_inherit = "stock.move"

	analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')

class stock_warehouse(models.Model):
	_inherit = "stock.warehouse"

	user_ids = fields.Many2many('res.users','company_user_rel','company_id','user_id','Owner user')