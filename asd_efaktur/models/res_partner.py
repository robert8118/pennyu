# -*- coding: utf-8 -*-
# Copyright 2023 PT Arkana Solusi Digital

from odoo import api, fields, models, tools, _

class res_partner(models.Model):
    _inherit = "res.partner"
    
    @api.onchange("npwp")
    def onchange_npwp(self):
        res = {}
        npwp = self.npwp
        if not npwp:
            return
        elif len(npwp) == 20:
            self.npwp = npwp
        elif len(npwp) == 15:
            formatted_npwp = npwp[:2] + "." + npwp[2:5] + "." + npwp[5:8] + "." + npwp[8:9] + "-" + npwp[9:12] + "." + npwp[12:15]
            self.npwp = formatted_npwp
        elif len(npwp) == 16:
            formatted_npwp = npwp[:2] + "." + npwp[2:5] + "." + npwp[5:8] + "." + npwp[8:9] + "-" + npwp[9:12] + "." + npwp[12:16]
            self.npwp = formatted_npwp
        else:
            warning = {
                "title": _("Warning"),
                "message": _("Wrong Format! Must 15 or 16 digit"),
            }
            return {"warning": warning, "value" : {"npwp" : False}}
        return res

    def _get_street_npwp(self):
        partner, partner_address = "", self
        if self.is_npwp:
            partner_address = self
        elif self.child_ids:
            addr_npwp = self.child_ids.filtered(lambda rec: rec.type == "npwp") or ""
            partner_address = addr_npwp
        elif self.parent_id and self.parent_id.child_ids:
            addr_npwp = self.parent_id.child_ids.filtered(lambda rec: rec.type == "npwp") or ""
            partner_address = addr_npwp
        if self.is_npwp_pribadi and self.alamat_npwp_pribadi:
            partner = self.alamat_npwp_pribadi
        else:
            if partner_address.street:
                partner += f"{partner_address.street}"
            if partner_address.street2:
                partner += f" {partner_address.street2}"
            if partner_address.blok:
                partner += f" {str(partner_address.blok)}"
            if partner_address.nomor:
                partner += f" {str(partner_address.nomor)}"
            if partner_address.rt:
                partner += f" {str(partner_address.rt)}"
            if partner_address.rw:
                partner += f" {str(partner_address.rw)}"
            if partner_address.kelurahan_id:
                partner += f" {partner_address.kelurahan_id.name}"
            if partner_address.kecamatan_id:
                partner += f" {partner_address.kecamatan_id.name}"
            if partner_address.kabupaten_id:
                partner += f" {partner_address.kabupaten_id.name}"
            if partner_address.state_id:
                partner += f" {partner_address.state_id.name}"
            if partner_address.zip:
                partner += f" {str(partner_address.zip)}"
            if partner_address.blok:
                partner += f" {str(partner_address.phone)}"
        return partner.upper()