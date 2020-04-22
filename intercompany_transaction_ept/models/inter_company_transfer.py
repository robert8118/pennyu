from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime
from lxml import etree
from odoo.addons import decimal_precision as dp

class intercompany_trasfer(models.Model):
    
    _name = "inter.company.transfer"
    #     _inherit = ['mail.thread']
    _order = 'create_date desc, id desc'
    
    
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    name = fields.Char('Name')
    
    source_warehouse_id = fields.Many2one('stock.warehouse', string='From Warehouse', required=True)
    source_company_id = fields.Many2one(related='source_warehouse_id.company_id', string="Source Company")
    
    crm_team_id = fields.Many2one('crm.team', string="Sales Team", default=_get_default_team)
    
    destination_warehouse_id = fields.Many2one('stock.warehouse', string='To Warehouse', required=True)
    destination_company_id = fields.Many2one(related='destination_warehouse_id.company_id', string="Destination Company")
    
    
    currency_id = fields.Many2one('res.currency', related="price_list_id.currency_id", string="Currency", required=True)
    price_list_id = fields.Many2one('product.pricelist', string="Price List")

    line_ids = fields.One2many('inter.company.transfer.line', 'transfer_id', string="Transfer Lines", copy=True)
    
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed'), ('cancel', 'Cancelled')], string='State', required=True, readonly=True, copy=False, default='draft')
    
    sale_order_ids = fields.One2many('sale.order', 'ict_id', sring='Sale Orders', copy=False)    
    purchase_order_ids = fields.One2many('purchase.order', 'ict_id', string="Purchase Order", copy=False)
    invoice_ids = fields.One2many('account.invoice', 'ict_id', String="Invoices", copy=False)
    processed_date = fields.Datetime("Processed Date", copy=False)
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)
    message = fields.Char("Message", copy=False)
    
    
    picking_ids = fields.One2many('stock.picking', 'ict_id', string="Pickings", copy=False)
    incoming_shipment_id = fields.Many2one('stock.picking', string="Incoming Shipment", copy=False)
    type = fields.Selection([('ict', 'ICT'), ('ict_reverse', 'Reverce ICT'), ('internal', 'Internal')], string='Type', required=True, readonly=True, copy=False, default='ict')
    _sql_constraints = [('src_dest_company_uniq', 'CHECK(source_warehouse_id!=destination_warehouse_id)', 'Source Warehouse and Destination warehouse must be different!')]
    
    
    # #Fields for ICT Reverse ##
    ict_id = fields.Many2one('inter.company.transfer', string="ICT")
    revesrse_ict_ids = fields.One2many('inter.company.transfer', 'ict_id', string="Reverse ICT")
    
    @api.model
    def create(self, vals):
        res = super(intercompany_trasfer, self).create(vals)
        
        if res.type == 'ict' or not res.type:
            res.write({'name':self.env.ref('intercompany_transaction_ept.ir_sequence_intercompany_transaction')._next()})
        elif res.type == 'ict_reverse':
            res.write({'name':self.env.ref('intercompany_transaction_ept.ir_sequence_reverse_intercompany_transaction')._next()})
        elif res.type == 'internal':
            res.write({'name':self.env.ref('intercompany_transaction_ept.ir_sequence_internal_transfer_intercompany_transaction')._next()})
        return res
    
    @api.onchange('source_warehouse_id')
    def source_warehouse_id_onchange(self):
        # self.destination_warehouse_id = False
        if not self.source_warehouse_id:
            self.destination_warehouse_id = False
            return
        if self.source_warehouse_id == self.destination_warehouse_id:
            self.destination_warehouse_id = False
        self.currency_id = self.source_company_id.currency_id
        
        res = {}
        if self.type == 'internal':
            domain = {'destination_warehouse_id':  [('company_id', '=', self.source_company_id.id), ('id', '!=', self.source_warehouse_id.id)]}
            return {'domain': domain}
        elif self.type != 'internal':
            domain = {'destination_warehouse_id':  [('company_id', '!=', self.source_company_id.id)]}
            return {'domain': domain}
        return res
    
    
    @api.onchange('destination_warehouse_id')
    def onchange_destination_warehouse_id(self):
        if not self.destination_warehouse_id:
            return False
        # self.price_list_id  = self.sudo(self.source_company_id.intercompany_user_id.id).destination_company_id.partner_id.property_product_pricelist
        self.price_list_id = self.destination_company_id.sudo().partner_id.sudo(self.source_company_id.intercompany_user_id.id).property_product_pricelist
        # self.crm_team_id = self.sudo(self.source_company_id.intercompany_user_id.id).destination_company_id.partner_id.team_id
        self.crm_team_id = self.destination_company_id.sudo().partner_id.sudo(self.source_company_id.intercompany_user_id.id).team_id
                  
        return 
    
    @api.multi
    def action_cancel(self):
        saleorder_ids = self.sale_order_ids.filtered(lambda so : so.state == 'draft')
        puchaseorder_ids = self.purchase_order_ids.filtered(lambda po:po.state == 'draft')
        invoice_ids = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        picking_ids = self.picking_ids.filtered(lambda pick:pick.state == 'draft')
        
        if self.state == 'processed':
            if saleorder_ids and puchaseorder_ids and invoice_ids and picking_ids:
                saleorder_ids.action_cancel()
                puchaseorder_ids.action_cancel()
                invoice_ids.action_cancel()
                picking_ids.action_cancel()
                self.reset_to_draft()
            else:
              raise  Warning("You Can not Cancel Inter Company Transaction Which All Transaction State is Done")
        else:
            self.write({'state':'cancel', 'message' : 'ICT has been cancelled by %s' % (self.env.user.name) })
        
  
    
    
    
    @api.multi
    def unlink(self):
        picking_ids = [picking.state != 'done' for picking in self.picking_ids]
        if picking_ids and self.state == 'processed':
            raise Warning("You can not delete transaction, if it is in Processed state !!")
        res = super(intercompany_trasfer, self).unlink()
        return res
    

    @api.multi  
    def open_attached_sale_order(self):
        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain':[('id', '=', self.sale_order_ids and self.sale_order_ids.ids or [])]
        }
    
    @api.multi
    def open_attached_purchase_order(self):
        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain':[('id', '=', self.purchase_order_ids and self.purchase_order_ids.ids or [])]
        }
        
    @api.multi
    def open_attached_reverse_ict(self):
        return {
            'name': _('Reverse ICT'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'inter.company.transfer',
            'domain':[('id', 'in', self.revesrse_ict_ids.ids)]
        }
    
    @api.multi
    def open_attached_invoice(self):
        tree_id = self.env.ref('account.invoice_tree').id
        form_id = self.env.ref('account.invoice_form').id
        invoices = self.env['account.invoice'].search([('ict_id', '=', self.id), ('type', '=', 'out_refund')]).ids
        return {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views':[(tree_id, 'tree'), (form_id, 'form')],
            'domain':[('id', 'in', invoices or [])]
        }
        
    @api.multi
    def open_attached_pickings(self):
        form_id = self.env.ref('stock.view_picking_form').id
        tree_id = self.env.ref('stock.vpicktree').id       
        return {
            'name':_('Pickings'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'views':[(tree_id, 'tree'), (form_id, 'form')],
            'domain':[('id', 'in', self.picking_ids and self.picking_ids.ids or [])]
            }
    
    @api.multi
    def open_attached_bill(self):
        tree_id = self.env.ref('account.invoice_supplier_tree').id
        form_id = self.env.ref('account.invoice_supplier_form').id
        invoices = self.env['account.invoice'].search([('ict_id', '=', self.id), ('type', '=', 'in_refund')]).ids
        return {
            'name': _('Vendor Bill'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views':[(tree_id, 'tree'), (form_id, 'form')],
            'domain':[('id', 'in', invoices or [])]
        }
        
    @api.multi
    def create_reverse_ict(self):
        reverse_ict_line_obj = self.env['reverse.ict.wizard.line']
        created_reverse_ids = []
       
        for line in self.line_ids:
            if line.qty_delivered != 0.0:
                qty_delivered = line.qty_delivered
                if line.qty_delivered <= line.quantity:
                    inter_company_transfer_ids = self.search([('ict_id', '=', self.id), ('type', '=', 'ict_reverse'), ('state', '!=', 'cancel')])
                    if inter_company_transfer_ids:
                        qty_delivered = 0.0
                        total_qty_delivered = 0.0
                        if len(inter_company_transfer_ids) > 1: 
                            for inter_company_id in inter_company_transfer_ids:
                                for transferline in inter_company_id.line_ids:
                                    if transferline.product_id == line.product_id:
                                        total_qty_delivered += transferline.quantity
                            qty_delivered = line.qty_delivered - total_qty_delivered 
                            if qty_delivered != 0.0 and qty_delivered > 0.0:
                                created_reverse_ids.append(reverse_ict_line_obj.create({'product_id':line.product_id.id, 'quantity':qty_delivered , 'qty_delivered': qty_delivered, 'price' : line.price}).id)
                        else:
                            for already_line in inter_company_transfer_ids.line_ids:
                                if already_line.product_id == line.product_id:
                                    if already_line.quantity == line.quantity:
                                        continue
                                    elif already_line.quantity < line.quantity:
                                        qty_delivered = line.qty_delivered - already_line.quantity 
                                        if qty_delivered != 0.0 and qty_delivered > 0.0:
                                            created_reverse_ids.append(reverse_ict_line_obj.create({'product_id':line.product_id.id, 'quantity':qty_delivered, 'qty_delivered': qty_delivered, 'price' : line.price}).id)
                                    else:
                                        created_reverse_ids.append(reverse_ict_line_obj.create({'product_id':line.product_id.id, 'quantity':qty_delivered , 'qty_delivered': qty_delivered, 'price' : line.price}).id)
                    else:
                        created_reverse_ids.append(reverse_ict_line_obj.create({'product_id':line.product_id.id, 'quantity':qty_delivered , 'qty_delivered': qty_delivered, 'price' : line.price}).id)      
                else:
                    continue
        
        if created_reverse_ids:
                return {             
                    'type': 'ir.actions.act_window',
                    'res_model': 'reverse.ict.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context' : {'default_ict_id':self.id, 'default_reverse_line_ids':[(6, 0, created_reverse_ids)],
                                 'default_destination_warehouse':self.destination_warehouse_id and self.destination_warehouse_id.id or False,
                                   },
                    'target': 'new',
                    
                }
        else:
            raise Warning("There are no products found for the Reverse Transaction  !!")
        
    
    @api.multi
    def _auto_create_sale_order(self):
       
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        res = []
        
        for record in self:
            source_company = record.source_company_id
            source_warehouse_id = record.source_warehouse_id
            intercompany_user = source_company.sudo().intercompany_user_id.id or False
            partner_id = record.destination_company_id.sudo().partner_id
            sale_order_vals = sale_obj.sudo(intercompany_user).new({'partner_id':partner_id.id, 'warehouse_id':source_warehouse_id.id, 'pricelist_id':self.price_list_id.id})
            sale_order_vals.sudo(intercompany_user).onchange_partner_id()
            sale_order_vals.warehouse_id = source_warehouse_id.id
            sale_order_vals.sudo(intercompany_user)._onchange_warehouse_id()
            sale_order_vals.fiscal_position_id = partner_id.sudo(intercompany_user).property_account_position_id.id
            sale_order_vals.pricelist_id = self.price_list_id.id
            if record.crm_team_id:
                sale_order_vals.team_id = record.crm_team_id.id
            sale_order_vals = sale_order_vals.sudo(intercompany_user)
            sale_order = sale_obj.sudo(intercompany_user).create(sale_order_vals._convert_to_write(sale_order_vals._cache))
            so_lines_vals = []
            for line in record.line_ids:
                so_line_vals = sale_line_obj.sudo(intercompany_user).new({'order_id':sale_order.id, 'product_id':line.product_id})
                so_line_vals.sudo(intercompany_user).product_id_change()
                so_line_vals.sudo(intercompany_user).product_uom_qty = line.quantity
                so_line_vals.price_unit = line.price
                so_line_vals = so_line_vals.sudo(intercompany_user)._convert_to_write(so_line_vals._cache)
                so_lines_vals.append((0, 0, so_line_vals))
            sale_order.sudo(intercompany_user).write({'order_line':so_lines_vals, 'ict_id':record.id})
            res.append(sale_order)
        
        return res        
    
    @api.multi
    def _auto_create_purchase_order(self):
       
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        res = []
        
        destination_company = self.destination_company_id
        intercompany_user = destination_company.sudo().intercompany_user_id.id or False
        
        for record in self:
            
            purchase_order_vals = purchase_obj.sudo(intercompany_user).new({'currency_id':self.currency_id.id, 'partner_id':record.source_warehouse_id.sudo().company_id.partner_id.id, 'company_id':destination_company.id})
            purchase_order_vals.sudo(intercompany_user).onchange_partner_id()
            purchase_order_vals.currency_id = self.currency_id.id
            purchase_order_vals.picking_type_id = self.destination_warehouse_id.sudo().in_type_id
            purchase_order = purchase_obj.sudo(intercompany_user).create(purchase_order_vals.sudo(intercompany_user)._convert_to_write(purchase_order_vals._cache))
            po_lines_vals = []
            for line in record.line_ids:
                po_line_vals = purchase_line_obj.sudo(intercompany_user).new({'order_id':purchase_order.id, 'product_id':line.product_id, 'currency_id':self.currency_id})
                po_line_vals.sudo(intercompany_user).onchange_product_id()
                po_line_vals.product_qty = line.quantity
                po_line_vals.price_unit = line.price 
                po_line_vals.product_uom = line.product_id.uom_id
                po_line_vals = po_line_vals.sudo(intercompany_user)._convert_to_write(po_line_vals._cache)
                po_lines_vals.append((0, 0, po_line_vals))
            purchase_order.sudo(intercompany_user).write({'order_line':po_lines_vals, 'ict_id':record.id})
            res.append(purchase_order)
        
        return res
    
    def validate_details(self):
        context = self._context or {}
        for record in self:
            if not record.source_warehouse_id.sudo().company_id.intercompany_user_id:
                msg = _('Please specify intercompany user for source company')
                if context.get('is_auto_validate', False):
                    record.write({'message':msg})
                    return False
                raise ValidationError(msg)
            
            if not record.destination_warehouse_id.sudo().company_id.intercompany_user_id:
                msg = 'Please specify intercompany user for destination company'
                if context.get('is_auto_validate', False):
                    record.write({'message':msg})
                    return False
                raise ValidationError(msg)
            
            if record.source_warehouse_id.sudo().company_id not in self.env.user.company_ids :
                if record.source_warehouse_id.sudo().company_id not in self.env.user.company_id.child_ids :
                    msg = "User '%s' can not process this Inter Company Transfer.\n User from Source Warehouse Company can Process it !!!!\n\nPlease Process it with User of Source Warehouse Company." % (self.env.user.name)
                    raise ValidationError(msg)
        return True
    
    @api.onchange('price_list_id')
    def default_price(self):
        for record in self:
            for line in record.line_ids:
                line.default_price_get()
        return
    
    @api.multi
    def reset_to_draft(self):
        self.ensure_one()
        self.state = 'draft'
    
    @api.multi
    def create_internal_transfer(self):
        picking_obj = self.env['stock.picking']
        source_wh = self.source_warehouse_id
        dest_wh = self.destination_warehouse_id
        self.env['stock.inventory.line']
        group_id = self.env['procurement.group'].create({
                    'name': self.name,
                    'partner_id': dest_wh.partner_id.id,
                })
        self.group_id = group_id.id
        route_ids = self.env['stock.location.route'].search([('supplied_wh_id', '=', dest_wh.id), ('supplier_wh_id', '=', source_wh.id)])
        if not route_ids:
            raise ValidationError(_("No routes are found. \n Please configure warehouse routes and set in products."))
        if not self.line_ids :
            raise ValidationError(_("No Products found. \n Please add products to transfer."))
        for line in self.line_ids:
            line_data = (0, 0, {
                'product_id':line.product_id.id,
                'product_uom':line.product_id.uom_id.id,
                'procure_method': 'make_to_stock',
                'product_uom_qty':line.quantity,
                'group_id': self.group_id and self.group_id.id,
                'name':line.product_id.name or '/',
                })
            self.env['procurement.group'].run(line.product_id, line.quantity, line.product_id.uom_id, dest_wh.lot_stock_id, self.name, False, values={'warehouse_id':dest_wh, 'route_ids':route_ids and route_ids[0], 'group_id':self.group_id, })

        pickings = picking_obj.search([('group_id', '=', group_id.id)])
        if not pickings:
            if not group_id:
                raise ValidationError(_("Problem with creation of procurement group."))
            else:
                raise ValidationError(_("NO Pickings are created for this record."))
        for picking in pickings:
            if not picking.ict_id:
                picking.ict_id = self.id
                picking.action_assign()
            picking_id = picking.search([('location_id', '=', self.source_warehouse_id.lot_stock_id.id)])
            if picking_id:
                picking_id.action_assign()
        return True

    @api.multi
    def validate_data(self):
        context = self._context.copy() or {}
        for record in self:
            if not record.with_context(context).validate_details():
                continue

            sale_user = record.sudo().source_company_id.intercompany_user_id.id
            purchase_user = record.sudo().destination_company_id.intercompany_user_id.id
            
            purchase_partner_id = record.source_company_id.sudo().partner_id
            
            config_record = record.env.ref('intercompany_transaction_ept.intercompany_transaction_config_record')
            invoice_obj = record.env['account.invoice']
            
            bypass = record._context.get('force_validate_picking', False)
            
            if  record.source_company_id == record.destination_company_id:
                if self.create_internal_transfer():
                    record.write({
                    'state':'processed',
                    'processed_date':datetime.today(),
                    'message':'ICT processed successfully by %s' % (self.env.user.name)
                    
                    })
                return
            
            sale_orders = record._auto_create_sale_order()
            purchase_orders = record._auto_create_purchase_order()
            
            if config_record:
                if config_record.auto_confirm_orders or bypass:
                    for sale_order in sale_orders:
                        sale_order.write({'origin':record.name or ''})
                        sale_order.sudo(sale_user).action_confirm()
#                         for pickings in sale_order.picking_ids:
#                             pickings.ict_id = self.id
                        if bypass:

                            if sale_order.picking_ids:
                                picking = sale_order.picking_ids[0]
                                picking.action_assign()

                                if picking.state in ['assigned']:
                                    validate_id = picking.do_new_transfer()
                                    res_id = validate_id.get('res_id')
                                    obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                                    transfer_id = obj_stock_immediate_transfer.browse(res_id)
                                    transfer_id.process()

                    for purchase_order in purchase_orders:
                        purchase_order.write({'origin':record.name or ''})
                       
                        purchase_order.sudo(purchase_user).button_confirm()
#                         for pickings in purchase_order.picking_ids:
#                             pickings.ict_id = self.id
                        if bypass:
                            purchase_order.picking_ids[0].action_assign()
                            validate_id = purchase_order.picking_ids[0].do_new_transfer()
                            res_id = validate_id.get('res_id')
                            obj_stock_immediate_transfer = self.env['stock.immediate.transfer']
                            transfer_id = obj_stock_immediate_transfer.browse(res_id)
                            transfer_id.process()
                        
                if config_record.auto_create_invoices:
                    invoice_id = False
                    
                    for sale_order in sale_orders:
                        context = {"active_model": 'sale.order', "active_ids": [sale_order.id], "active_id": sale_order.id, 'open_invoices':True}
                        if record.source_company_id.sale_journal:
                            context.update({'default_journal_id':record.source_company_id.sale_journal.id})
                        payment = record.env['sale.advance.payment.inv'].sudo(sale_user).create({
                                    'advance_payment_method': 'delivered',
                                })
                        result = payment.with_context(context).sudo(sale_user).create_invoices()
                        result = result.get('res_id', False)
                        invoice_id = record.env['account.invoice'].sudo(sale_user).browse(result)
                        invoice_id.sudo(sale_user).write({'date_invoice':datetime.today(), 'ict_id':self.id})
                    
                    bill_id = False
                    for purchase_order in purchase_orders:
                        context = {'default_type': 'in_invoice',
                                    'type': 'in_invoice',
                                    'journal_type': 'purchase',
                                    'default_purchase_id': purchase_order.id
                                }
                        if record.destination_company_id.purchase_journal:
                            context.update({'default_journal_id':record.destination_company_id.purchase_journal.id})
                        
                        values = {
                            'company_id': record.destination_company_id.id or False,
                            'currency_id':record.currency_id,
                            'partner_id':purchase_partner_id.id,
                            'type': 'in_invoice',
                            'journal_type': 'purchase',
                            'purchase_id': purchase_order.id
                        }
                        
                        vals = invoice_obj.sudo(purchase_user).with_context(context).new(values)
                        vals.purchase_id = purchase_order.id
                        vals.journal_id = vals.sudo(purchase_user)._default_journal()
                        vals.sudo(purchase_user).purchase_order_change()
                        vals.sudo(purchase_user)._onchange_partner_id()
                        vals.date_invoice = datetime.today()
                        vals.sudo(purchase_user)._onchange_payment_term_date_invoice()
                        vals.sudo(purchase_user)._onchange_origin()
                        vals.currency_id = record.currency_id
                        
                        for line in vals.invoice_line_ids:
                            line.quantity = line.purchase_line_id and line.purchase_line_id.product_qty or 0.0
                            line.sudo(purchase_user)._compute_price()
                            
                        bill_id = record.env['account.invoice'].sudo(purchase_user).with_context({'type':'in_invoice'}).create(vals._convert_to_write(vals._cache))
                        bill_id.ict_id = self.id
                    
                    if config_record.auto_validate_invoices:
                        invoice_id.sudo(sale_user).action_invoice_open()
                        bill_id.sudo(purchase_user).action_invoice_open()
                        
            record.write({
                'state':'processed',
                'processed_date':datetime.today(),
                'message':'ICT processed successfully by %s' % (self.env.user.name)
                })
            
    @api.multi
    def process_reverse_ict(self):
        
        stock_return_picking = self.env['stock.return.picking']
        account_invoice_refund = self.env['account.invoice.refund']
        stock_move_obj = self.env['stock.move']
        picking_to_stock = []
        pickings = [] 
        internal_transfer = False
        if not self.line_ids:
            raise ValidationError(_("There are no products in the record!!"))
        
        # REVERSE INTERNAL TRASFER ##
        if not self.ict_id.sale_order_ids and not self.ict_id.purchase_order_ids:
            pickings = self.ict_id.picking_ids
            if not pickings:
                raise ValidationError(_("There are no pikings available in %s " % self.ict_id.name))
            if not pickings.filtered(lambda pc : pc.state == 'done'):
                raise ValidationError(_("%s have some pickings which are not in done state yet!! \n Please done pickings befor reverse it. " % self.ict_id.name))
            internal_transfer = True
        
        if internal_transfer:
            processed = False
            
            for picking in pickings:
                picking_to_stock = []
                for line in self.line_ids:
                    for move_id in stock_move_obj.search([('picking_id', '=', picking.id), ('product_id', '=', line.product_id.id), ('state', '=', 'done')]):
                        line_tmp = (0, 0, {'product_id': move_id.product_id.id, 'move_id': move_id.id, 'quantity': line.quantity, 'to_refund': False})
                        picking_to_stock.append(line_tmp)
                default_vals = stock_return_picking.with_context({'active_id':picking.id}).default_get(['move_dest_exists', 'original_location_id', 'parent_location_id', 'location_id', 'product_return_moves'])
                default_vals.update({'product_return_moves':picking_to_stock})
                return_picking = stock_return_picking.with_context({'active_ids':[]}).create(default_vals)
                tmp = return_picking.with_context({'active_id':move_id.picking_id.id}).create_returns()
                stock_picking = self.env['stock.picking'].browse(tmp.get('res_id'))
                if stock_picking:
                    for picking in stock_picking:
                        picking.ict_id = self.id
                    processed = True
            if processed:
                self.write({'state':'processed'})
                return True
            return False
        
        # REVERSE INTERCOMPANY TRASFER ##
        # #Reverse so moves
        pickings = []
        if self.ict_id.sale_order_ids:
            for sale_order in self.ict_id.sale_order_ids:
                pickings += sale_order.picking_ids and sale_order.picking_ids.filtered(lambda pck : pck.picking_type_id.code == 'outgoing')
            if not pickings:
                raise ValidationError(_("No pickings are available in sale order"))
        for picking in pickings:
            for line in self.line_ids:
                for move_id in stock_move_obj.search([('picking_id', '=', picking.id), ('product_id', '=', line.product_id.id), ('state', '=', 'done')]):
                    line_tmp = (0, 0, {'product_id': move_id.product_id.id, 'move_id': move_id.id, 'quantity': line.quantity, 'to_refund': False})
                    picking_to_stock.append(line_tmp)
         
            default_vals = stock_return_picking.with_context({'active_id':picking.id}).default_get(['move_dest_exists', 'original_location_id', 'parent_location_id', 'location_id', 'product_return_moves'])
            
            default_vals.update({'product_return_moves':picking_to_stock})
            return_picking = stock_return_picking.with_context({'active_id':picking.id}).create(default_vals)
        
            tmp = return_picking.with_context({'active_id':picking.id}).create_returns()
            stock_picking = self.env['stock.picking'].browse(tmp.get('res_id'))

            if stock_picking:
                stock_picking.ict_id = self.id
        
        incoming_picking_to_stock = []
        incoming_pickings = []
        if self.ict_id.purchase_order_ids:
            for purchase_order in self.ict_id.purchase_order_ids:
                incoming_pickings += purchase_order.picking_ids and purchase_order.picking_ids.filtered(lambda pck : pck.picking_type_id.code == 'incoming')
        for incoming_picking in incoming_pickings:
            for line in self.line_ids:
                for move_id in stock_move_obj.search([('picking_id', '=', incoming_picking.id), ('product_id', '=', line.product_id.id), ('state', '=', 'done')]):
                    line_tmp = (0, 0, {'product_id': move_id.product_id.id, 'move_id': move_id.id, 'quantity': line.quantity})
                    incoming_picking_to_stock.append(line_tmp)
    
            default_incoming_vals = stock_return_picking.with_context({'active_id':incoming_picking.id}).default_get(['move_dest_exists', 'original_location_id', 'parent_location_id', 'location_id', 'product_return_moves'])
            default_incoming_vals.update({'product_return_moves':incoming_picking_to_stock})
            return_incoming_picking = stock_return_picking.with_context({'active_ids':[]}).create(default_incoming_vals)
            tmp = return_incoming_picking.with_context({'active_id':incoming_picking.id}).create_returns()
            stock_picking = self.env['stock.picking'].browse(tmp.get('res_id'))
        
            if stock_picking:
                stock_picking.ict_id = self.id
        
        
        # REFUND CUSTOMER INVOICE ##
        customer_invoice_id = False
        customer_invoices = []
        for sale_order in self.ict_id.sale_order_ids:
            for invoice in sale_order.invoice_ids.filtered(lambda inv : inv.type == 'out_invoice'):
                customer_invoice_id = invoice.search([('refund_invoice_id', '=', invoice.id)], order='id desc' , limit=1)
#                 if not customer_invoice_id:
                default_inovoice_vals = account_invoice_refund.with_context({'active_id':invoice.id}).default_get(['filter_refund', 'description', 'date_invoice', 'date'])
                # configuration record
                
                config_record = self.env.ref('intercompany_transaction_ept.intercompany_transaction_config_record')
                if config_record.filter_refund:
                    default_inovoice_vals['filter_refund'] = config_record.filter_refund
                default_inovoice_vals.update({'description':'%s' % (config_record and config_record.description or ('for %s' % self.name))})
                cust_refund = account_invoice_refund.with_context({'active_id':invoice.id}).create(default_inovoice_vals)
                
                if cust_refund.with_context({'active_ids':invoice.id}).invoice_refund():
                    invoice_id = customer_invoice_id.search([('refund_invoice_id', '=', invoice.id)], order='id desc', limit=1)
                    if invoice_id:
                        invoice_id.ict_id = self.id
                        for invoice_line in invoice_id.invoice_line_ids:
                            match_line = self.line_ids.filtered(lambda ln : ln.product_id.id == invoice_line.product_id.id)
                            if match_line:
                                invoice_line.quantity = match_line.quantity
                        if invoice_id.state == "draft":
                            invoice_id = invoice_id.with_context({'active_ids':invoice.id}).action_invoice_open()

        # ASK FOR REFUND VENDOR BILL ##
        vendor_bill_id = False
        for purchase_order in self.ict_id.purchase_order_ids:
            for vendor_bill in purchase_order.invoice_ids.filtered(lambda inv : inv.type == 'in_invoice'):
                vendor_bill_id = vendor_bill.search([('refund_invoice_id', '=', vendor_bill.id)], order='id desc' , limit=1)
#                 if not vendor_bill_id:
                default_inovoice_vals = account_invoice_refund.with_context({'active_id':vendor_bill.id}).default_get(['filter_refund', 'description', 'date_invoice', 'date'])
                # configuraion record #
                config_record = self.env.ref('intercompany_transaction_ept.intercompany_transaction_config_record')
                if config_record.filter_refund:
                        default_inovoice_vals['filter_refund'] = config_record.filter_refund
                default_inovoice_vals.update({'description':'%s' % (config_record and config_record.description or ('for %s' % self.name))})
                vendor_refund = account_invoice_refund.with_context({'active_id':vendor_bill.id}).create(default_inovoice_vals)
                invoice_id = False
                if vendor_refund.with_context({'active_ids':vendor_bill.id}).invoice_refund():
                    invoice_id = customer_invoice_id.search([('refund_invoice_id', '=', vendor_bill.id)], order='id desc', limit=1)
                    if invoice_id:
                        invoice_id.ict_id = self.id
                        for invoice_line in invoice_id.invoice_line_ids:
                            match_line = self.line_ids.filtered(lambda ln : ln.product_id.id == invoice_line.product_id.id)
                            if match_line:
                                invoice_line.quantity = match_line.quantity
                        if invoice_id.state == "draft":
                            invoice_id = invoice_id.with_context({'active_ids':vendor_bill.id}).action_invoice_open()
#         if vendor_bill_id and customer_invoice_id:
        self.write({'state':'processed'})
        return True
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        context = self._context
        res = super(intercompany_trasfer, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree']:
            if context.get('type', 'ict_reverse') == 'ict_reverse':
                for node in doc.xpath("//tree[@string='Intercompany Transaction']"):
                    node.set('create', 'false')
                for node in doc.xpath("//form[@string='Inter Company Transaction']"):
                    node.set('create', 'false')
            res['arch'] = etree.tostring(doc)
        return res
    
    
    
    @api.multi
    def import_export_product_list_view(self):
        form_id = self.env.ref('intercompany_transaction_ept.import_export_product_list_ept_form_view').id
        ctx = self._context.copy() or {}
        ctx.update({'record':self.id or False})
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.export.product.list.ept',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
                'context': ctx,
                }
    
class intercompany_trasfer_line(models.Model):
    _name = "inter.company.transfer.line"


    @api.depends( 'transfer_id.picking_ids.state')
    def _get_delivered_qty(self):
         for line in self:
            if line.transfer_id.state in ['processed']:
                qty_delivered = 0.0
                for picking_id in line.transfer_id.picking_ids:
                    if picking_id.state != 'cancel':
                        for move_line in picking_id.move_lines:
                            if line.product_id == move_line.product_id:
                                if picking_id.picking_type_id.code == 'incoming':
                                        qty_delivered += move_line.product_id.uom_id._compute_quantity(move_line.quantity_done, move_line.product_id.uom_id)
                            line.qty_delivered = qty_delivered
            else:
                line.qty_delivered = 0.0


    product_id = fields.Many2one('product.product', 'Product', required=True)
    qty_delivered = fields.Float(compute='_get_delivered_qty', string='Delivered Quantity', store=True, readonly=True, digits=dp.get_precision('Product Unit of Measure'))
    quantity = fields.Float("Quantity", required=True, default=1.0)
    price = fields.Float('Price')
    transfer_id = fields.Many2one('inter.company.transfer')
    
    @api.onchange('product_id', 'transfer_id')
    def default_price_get(self):
        """
        Get the Product Price
        """
        for record in self:
            product_id = record.product_id
            if product_id:
                pricelist_id = record.transfer_id.price_list_id
                if pricelist_id:
                    record.price = pricelist_id.price_get(product_id.id, record.quantity)[pricelist_id.id]
                else:
                    record.price = record.product_id.lst_price
            else:
                record.price = 0.0
            
