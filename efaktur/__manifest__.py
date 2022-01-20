{
    "name"          : "E-Faktur",
    "version"       : '11.0.3.0.2',
    'license'       : 'AGPL-3',
    'summary'       : 'Efaktur Import for DJP',
    "depends"       : [
                       #"account", 
                       'msi_partner',
                       "aos_base_account",
                       "aos_l10n_id", 
                       "aos_account_discount",
                       #"mail_attach_existing_attachment"
                       ],
    'external_dependencies': {'python': ['xlwt']},
    'images':  ['images/main_screenshot.png'],
    "author"        : "Alphasoft",
    "description"   : """This module aim to:
                    - efaktur djp 3.1.0.0
                    - Create Object Nomor Faktur Pajak
                    - Add Column Customer such as: 
                        * NPWP, RT, RW, Kelurahan, Kecamatan, Kabupaten, Province
                    - Just Import the file csv at directory data
                    - Export file csv for upload to efaktur
                    - Support multi company""",
    "website"       : "https://www.alphasoft.co.id/",
    "category"      : "Accounting",
    "data"    : [
                "security/ir.model.access.csv",
                'security/account_security.xml',
                #"data/res_country_data.xml",
                "views/base_view.xml",
                "views/res_partner_view.xml",                
                'views/res_config_settings_views.xml',
                "wizard/faktur_pajak_inv_view.xml",
                "views/faktur_pajak_view.xml",
                "views/account_invoice_view.xml",
                "wizard/faktur_pajak_generate.xml",
                "wizard/faktur_pajak_upload.xml",
                "wizard/fp_product_view.xml",
                "wizard/fp_partner_view.xml",
                "wizard/fp_invoice_view.xml",
    ],
    'price'         : 299.00,
    'currency'      : 'EUR',
    "init_xml"      : [],
    "demo_xml"      : [],
    'test'          : [],    
    "active"        : False,
    "installable"   : True,
    'application'   : False,
    #'post_init_hook': '_post_init',
}