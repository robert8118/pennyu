{
    'name': "Pennyu - PoS Disallow Negative Stock",
    'summary': """
        Validate negative stock products at Point of Sale (only for products that do not allow negative stock).""",
    'author': "PT Arkana Solusi Digital",
    'website': "http://www.arkana.co.id",
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ['point_of_sale', 'stock_no_negative'],
    'data': [
        'views/templates.xml',
    ],
}
