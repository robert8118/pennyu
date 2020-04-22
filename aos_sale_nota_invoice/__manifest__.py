# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2017 Alphasoft
#    (<https://www.alphasoft.co.id/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Nota Invoice',
    'version': '11.0.0.1.0',
    'sequence': 1,
    'summary': 'Example of a module by Alphasoft.',
    'author': "Alphasoft",
    'website': 'https://www.alphasoft.co.id/',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'images':  ['images/main_screenshot.png'],
    'description': 'Module based on Alphasoft',
    'depends': [
                'sale',
                'account', 
                'pn_sale', 
                'pn_account'
                ],
    'data': [            
            'views/sale_order_view.xml',
            'report/paperformat.xml',
            'report/sale_nota_report.xml',
     ],
    'demo': [],
    'test': [],
    'qweb': [],
    'css': [],
    'js': [],
    'installable': True,
    'auto_install': False,
}
