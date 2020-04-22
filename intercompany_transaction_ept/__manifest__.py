{
   
    # App information
   
    'name': 'Inter Company Transfer and Warehouse Transfer',
    'version': '11.0',
    'category': 'stock',
    'license': 'OPL-1',
    'summary' : 'Module to manage Inter Company Transfer and Inter Warehouse Transfer along with all required documents with easiest way by just simple configurations.',
    
		 
	# Author
			
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
    
    # Dependencies 
   
    'depends': ['delivery', 'sale', 'purchase', 'stock'],
    'data': [
            'data/ir_sequence.xml',
            'data/intercompany_config.xml',
            'views/configuration.xml',
            'views/intecompany_transaction.xml',
            'views/res_company.xml',
            'views/sale_order.xml',
            'views/purchase_order.xml',
            'views/stock_picking.xml',
            'reports/report.xml',
            'wizard/reverse_ict_wizard.xml',
            'wizard/import_export_product_list_views.xml',
            'views/ict_process_log_views.xml',
            'security/ICT_security.xml',
            'security/ir.model.access.csv',
            
             ],

      # Odoo Store Specific       
     'images': ['static/description/Inter-Company-Transfer-cover.png'],
              
    # Technical
    'post_init_hook': 'post_init_update_rule',
    'uninstall_hook': 'uninstall_hook_update_rule', 
    'external_dependencies' : {'python' : ['openpyxl', 'xlrd','xlwt'], },
    'live_test_url': 'http://bit.ly/2M3GMH9',
    'active': True,
    'installable': True,
    'currency': 'EUR',
    'price': 149.00,
    'auto_install': False,
    'application': True,
}
