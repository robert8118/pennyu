{
    'name': 'Purchase Order Template (Qweb) - Pennyu',
    'version': '11.0.1.0.2',
    'category': 'Purchase',
    'depends': ['purchase',
                'efaktur',
                'report_qweb_element_page_visibility',
                ],
    'author': 'Portcities Ltd',
    'summary': 'Custom Purchase Order Template',
    'data': [
        'reports/purchase_report.xml',
        'reports/purchase_order_template.xml',
        ],
    'description': """
    v.1.0.0
        Author : Ugi \n
        - Custom Purchase Order template
    """,
    'qweb': [],
    'website': 'https://www.portcities.net',
    'image': [],
    'auto_install': False,
    'installable': True,
    'application': False,
}
