{
    'name': "Pennyu - Master Data Work Location",
    'summary': """
        Work location master data for employee module""",
    'description': """""",
    'author': "PT Arkana Solusi Digital",
    'website': "http://www.arkana.co.id",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_views.xml',
        'views/hr_work_location_views.xml',
    ],
}
