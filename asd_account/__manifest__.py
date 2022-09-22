    # -*- coding: utf-8 -*-
{
    'name': "PENNYU Account",
    'summary': """
        Account for PENNYU V11 EE""",
    'author': "PT. Arkana Solusi Digital",
    'website': "http://www.arkana.co.id",
    'category': 'Account',
    'version': '0.1',
    'depends': ['account','payment'],
    'data': [
        'data/data.xml',
        # 'data/ir_cron.xml',
        # 'views/account_move_views.xml',
        'views/account_payment_views.xml',
    ],
}
