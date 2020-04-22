# pylint: disable=C0111,W0104
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright © PT PCI BUSINESS SOLUTION. (<https://www.portcities.net>).
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
    'name': 'POS Print - Pennyu',
    'version': '11.0.1.0.0',
    'category': 'Point Of Sale',
    'depends': ['point_of_sale'],
    'author': 'Portcities Ltd',
    'summary': 'Custom Print on POS',
    'data': [
        ],
    'description': """
    v.1.0.0
        Author : Andrew Y K\n
        - Add new features:
            - template receipt pennyu
    """,
    'qweb': ['static/src/xml/pos.xml'],
    'website': 'https://www.portcities.net',
    'data' : ['views/template.xml'],
    'image': [],
    'auto_install': False,
    'installable': True,
    'application': False,
}
