#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

print "#################################################################"
print "# Simple is an application to generate Module for Odoo ERP      #"
print "# www.alphasoft.co.id                                           #"
print "# Autor: Alphasoft                                              #"
print "# mail: odoo@alphasoft.co.id                                    #"
print "#################################################################"

# Entramos el nombre del módulo
name = raw_input("Enter the Module Name : ")
depends = raw_input("Enter the Module Depends ex: 'base','account' : ")
new_object = raw_input("Enter New Object : ")
if new_object:
    count_field = int(raw_input("Number of Fields : "))
    print ""
    print "###############  Add Field ##############################"
    print ""
inherit_object = raw_input("Enter Inherit Object : ")
# Create Folder
os.makedirs(name)
os.makedirs(name+"/views")
os.makedirs(name+"/models")
os.makedirs(name+"/report")
os.makedirs(name+"/security")
os.makedirs(name+"/static")
os.makedirs(name+"/static/description")

# Create __init__.py
file = open(name + '/__init__.py','w')
file.write('# -*- coding: utf-8 -*- \n')
file.write('from . import models \n')
file.close()


# Create el __manifest__.py
file = open(name + '/__manifest__.py','w')
file.write('# -*- coding: utf-8 -*-\n')
file.write('##############################################################################\n')
file.write('#\n')
file.write('#    OpenERP, Open Source Management Solution\n')
file.write('#    This module copyright (C) 2017 Alphasoft\n')
file.write('#    (<https://www.alphasoft.co.id/>).\n')
file.write('#\n')
file.write('#    This program is free software: you can redistribute it and/or modify\n')
file.write('#    it under the terms of the GNU Affero General Public License as\n')
file.write('#    published by the Free Software Foundation, either version 3 of the\n')
file.write('#    License, or (at your option) any later version.\n')
file.write('#\n')
file.write('#    This program is distributed in the hope that it will be useful,\n')
file.write('#    but WITHOUT ANY WARRANTY; without even the implied warranty of\n')
file.write('#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n')
file.write('#    GNU Affero General Public License for more details.\n')
file.write('#\n')
file.write('#    You should have received a copy of the GNU Affero General Public License\n')
file.write('#    along with this program.  If not, see <http://www.gnu.org/licenses/>.\n')
file.write('#\n')
file.write('##############################################################################\n')
file.write('{\n')
file.write('    \'name\': \'' + name + '\',\n')
file.write('    \'version\': \'11.0.0.1.0\',\n')
file.write('    \'sequence\': 1,\n')
file.write('    \'summary\': \'Example of a module by Alphasoft.\',\n')
file.write('    \'author\': "Alphasoft",\n')
file.write('    \'website\': \'https://www.alphasoft.co.id/\',\n')
file.write('    \'license\': \'AGPL-3\',\n')
file.write('    \'category\': \'Accounting\',\n')
file.write('    \'description\': \'Module based on Alphasoft\',\n')
file.write('    \'depends\': ['+ depends +'],\n')
file.write('    \'data\': [\n')
file.write('            \'report/report_view.xml\',\n')
if new_object:
    file.write('            \'views/'+ new_object.replace('.','_') + '_view.xml\',\n')
if inherit_object:
    file.write('            \'views/'+ inherit_object.replace('.','_') + '_view.xml\',\n')
file.write('     ],\n')
file.write('    \'demo\': [],\n')
file.write('    \'test\': [],\n')
file.write('    \'qweb\': [],\n')
file.write('    \'css\': [],\n')
file.write('    \'js\': [],\n')
file.write('    \'installable\': True,\n')
file.write('    \'auto_install\': False,\n')
file.write('}\n')
file.close()

# Import Models
file = open(name + '/models/__init__.py','w')
file.write('# -*- coding: utf-8 -*- \n')
if new_object:
    file.write('from . import '+new_object.replace('.','_')+' \n')
if inherit_object:
    file.write('from . import '+inherit_object.replace('.','_')+' \n')
file.close()

# Create Models
if new_object:
    file = open(name + '/models/'+new_object.replace('.','_')+'.py','w')
    file.write('# -*- coding: utf-8 -*- \n')
    file.write('# Part of Odoo. See LICENSE file for full copyright and licensing details. \n')
    file.write('from odoo import api, fields, models \n')
    file.write('from datetime import datetime \n')
    file.write('\n')
    file.write('class '+new_object.replace('.','_')+'(models.Model): \n')
    file.write('    _name = \''+new_object+'\' \n')
    fnames = []
    for num in range(1,count_field+1):
        fname = raw_input("Field Name: ")
        print "Char,Text,Boolean,Datetime,Integer"
        ftipo = raw_input("Field Type: ")
        print "-----------------------------------"
        file.write('    '+fname+' = fields.'+ftipo+'(string=\''+fname+'\', required=True) \n')
        file.write(' \n')
        fnames.append(fname)
    file.close()
    # Create _views.xml
    file = open(name + '/views/'+ new_object.replace('.','_') + '_view.xml','w')
    file.write('<?xml version="1.0" encoding="UTF-8"?> \n')
    file.write('<odoo> \n')
    file.write('     <record id="view_aos_' + new_object.replace('.','_') + '_form" model="ir.ui.view"> \n')
    file.write('        <field name="name">' + new_object + '.form</field> \n')
    file.write('        <field name="model">' + new_object + '</field> \n')
    file.write('        <field name="arch" type="xml"> \n')
    file.write('            <form string="List of '+new_object.replace('.',' ').capitalize()+'"> \n')
    file.write('                <group> \n')
    for fname in fnames:
        file.write('                    <field name="'+fname+'"/> \n')
    file.write('                </group> \n')
    file.write('            </form> \n')
    file.write('        </field> \n')
    file.write('    </record> \n')
    
    file.write('     <record id="view_aos_' + new_object.replace('.','_') + '_tree" model="ir.ui.view"> \n')
    file.write('        <field name="name">' + new_object + '.tree</field> \n')
    file.write('        <field name="model">' + new_object + '</field> \n')
    file.write('        <field name="arch" type="xml"> \n')
    file.write('           <tree> \n')
    for fname in fnames:
        file.write('           <field name="'+fname+'"/> \n')
    file.write('           </tree> \n')
    file.write('        </field> \n')
    file.write('    </record> \n')
    
    # Create Action
    file.write('    <record model="ir.actions.act_window" id="act_aos_' + new_object.replace('.','_') + '"> \n')
    file.write('        <field name="name">' + new_object + '</field> \n')
    file.write('        <field name="type">ir.actions.act_window</field> \n')
    file.write('        <field name="res_model">' + new_object + '</field> \n')
    file.write('        <field name="view_type">form</field> \n')
    file.write('        <field name="view_mode">tree,form</field> \n')
    file.write('    </record> \n')
    
    # Creat Menu
    file.write('    <!--  menu --> \n')
    file.write('    <menuitem id="aos_' + new_object.replace('.','_') + '_menu" name="' + new_object.replace('.',' ').capitalize() + '" sequence="10"/> \n')
    file.write('    <menuitem id="submenu_aos_' + new_object.replace('.','_') + '_menu" name="'+ new_object.replace('.',' ').capitalize() +'" sequence="10" parent="aos_' + new_object.replace('.','_') + '_menu"/> \n')
    file.write('    <menuitem id="submenu_aos_' + new_object.replace('.','_') + '_action" name="'+ new_object.replace('.',' ').capitalize() + '" sequence="10" parent="submenu_aos_' + new_object.replace('.','_') + '_menu" action="act_aos_' + new_object.replace('.','_') + '"/> \n')
    
    file.write('</odoo> \n')
    file.close()
    # Create ir.module.access.py
    file = open(name + '/security/ir.model.access.csv','w')
    file.write('id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n')
    file.write('access_'+new_object.replace('.','_')+'_user'+','+new_object+',model_'+new_object.replace('.','_')+',,1,1,1,0\n')
    file.close()
# Create Models
if inherit_object:
    file = open(name + '/models/'+inherit_object.replace('.','_')+'.py','w')
    file.write('# -*- coding: utf-8 -*- \n')
    file.write('# Part of Odoo. See LICENSE file for full copyright and licensing details. \n')
    file.write('from odoo import api, fields, models \n')
    file.write('from datetime import datetime \n')
    file.write('\n')
    file.write('class '+inherit_object.replace('.','_')+'(models.Model): \n\n')
    file.write('    _inherit = \''+inherit_object+'\' \n')
    file.close()
    # Create _views.xml
    file = open(name + '/views/'+ inherit_object.replace('.','_') + '_view.xml','w')
    file.write('<?xml version="1.0" encoding="utf-8"?>\n')
    file.write('<odoo>\n')
    file.write('    <data> \n\n')
    file.write('    </data>\n')
    file.write('</odoo> \n')
    file.close()
    
file = open(name + '/report/report_view.xml','w')
file.write('<?xml version="1.0" encoding="utf-8"?>\n')
file.write('<odoo>\n')
file.write('    <data> \n')
file.write('        <!-- Its just example QWeb Reports --> \n')
file.write('        <!-- \n')
file.write('        <report\n')
file.write('            id="account_invoices"\n')
file.write('            model="account.invoice"\n')
file.write('            string="Invoices"\n')
file.write('            report_type="qweb-pdf"\n')
file.write('            name="account.report_invoice"\n')
file.write('            file="account.report_invoice"\n')
file.write('            attachment_use="False"\n')
file.write('        />\n')
file.write('        -->\n')
file.write('    </data>\n')
file.write('</odoo> \n')
file.close()

print "\nThe module was created: " + name





