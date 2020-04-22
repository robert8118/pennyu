# pylint: disable=E0401,R0903
# -*- coding: utf-8 -*-
"""Inherit res.users"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    """Inherit res.users"""
    _inherit = "res.users"

    authorize_discount_pos = fields.Boolean(string = "Authorize Discount PoS")
    authorize_password = fields.Char(string = "Authorize Password", compute="_compute_pin_password",size=32)

    @api.constrains('authorize_password')
    def _check_pin(self):
        if self.authorize_password and not self.authorize_password.isdigit():
            raise UserError(_("Authorize Password can only contain digits"))

    @api.depends('pos_security_pin')
    def _compute_pin_password(self):
        for record in self:
            if record.pos_security_pin:
                if not record.pos_security_pin.isdigit():
                    raise UserError(_("Pos Security Pin can only contain digits"))
                elif record.authorize_discount_pos and record.pos_security_pin.isdigit():
                    record.authorize_password = record.pos_security_pin

