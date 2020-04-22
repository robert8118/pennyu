# -*- coding: utf-8 -*-
"""pn_account/account_journal"""

from odoo import models, fields


class AccountJournal(models.Model):
    """inherit model account.journal"""
    _inherit = 'account.journal'

    display_on_footer = fields.Boolean('Show in Invoice Footer')
