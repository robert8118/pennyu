# -*- coding: utf-8 -*-
# Copyright 2024 PT Arkana Solusi Digital
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': "Pennyu - Limit Requested Date",
    'summary': """Limit Sale Order Requested Date""",
    'category': 'Sales',
    'author': "PT. Arkana Solusi Bisnis",
    'website': "http://www.arkana.co.id",
    'version': '0.1',
    'depends': [
        'asb_sale',
        'sale_order_dates',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
