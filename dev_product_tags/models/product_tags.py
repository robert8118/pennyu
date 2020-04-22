# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class product_tags(models.Model):
	_name = 'product.tags'
	
	name = fields.Char(string="Tag Name",required="1")
	
class product_template(models.Model):
    _inherit = 'product.template'
    
    tag_ids = fields.Many2many('product.tags',string='Tags')
	

	




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
