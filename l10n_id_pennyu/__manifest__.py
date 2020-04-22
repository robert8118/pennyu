# -*- coding: utf-8 -*-
##############################################################################
#
# This module is developed by Portcities Indonesia
# Copyright (C) 2017 Portcities Indonesia (<http://idealisconsulting.com>).
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Indonesian - Setting for Accounting',
    'version': '1.0',
    'category': 'Localization',
    'description': """
Indonesian Accounting Module
============================

Indonesian accounting basic charts and localizations.

Also:
    - activates a number of regional currencies.
    - sets up Indonesian taxes.
""",
    'author': 'Port Cities Indonesia',
    'website': 'http://www.portcities.net',
    'depends': [ 'base', 'account','base_iban', 'base_vat'],
    'data': [
        'data/l10n_id_chart_data.xml',
        'data/account.account.template.csv',
        'data/account.chart.template.csv',
        'data/account.account.tag.csv',
        'data/account.tax.template.csv',
        'data/account_chart_template_data.yml',
    ],
}
