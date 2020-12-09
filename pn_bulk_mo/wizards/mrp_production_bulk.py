from odoo import api, fields, models


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, vals):
        @api.model
        def create(self, vals):
            if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
                dups = self.env['mail.followers'].search([('res_model', '=', vals.get('res_model')),
                                                          ('res_id', '=', vals.get('res_id')),
                                                          ('partner_id', '=', vals.get('partner_id'))])
                if len(dups):
                    for p in dups:
                        p.unlink()
            return super(MailFollowers, self).create(vals)


class MrpProductionBulk(models.TransientModel):
    _name = 'mrp.production.bulk'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            (
                'warehouse_id.company_id', 'in',
                [self.env.context.get('company_id', self.env.user.company_id.id), False]
            )], limit=1).id

    date_produce = fields.Date('Manufacture Date')
    mo_shift = fields.Many2one('mrp.shift', 'Shift')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',
                                      default=_get_default_picking_type)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'mrp.production.bulk'))
    location_src_id = fields.Many2one('stock.location', 'Raw Material Location',
                                      related='picking_type_id.default_location_src_id')
    location_dest_id = fields.Many2one('stock.location', 'Finished Product Location',
                                       related='picking_type_id.default_location_dest_id')
    lines_id = fields.One2many(comodel_name="mrp.production.bulk.line", inverse_name="line_id", string="Lines")

    def create_bulk_mo(self):
        mp = self.env['mrp.production']
        data = {
            'mo_shift': self.mo_shift.id,
            'user_id': self.user_id.id,
            'picking_type_id': self.picking_type_id.id,
            'company_id': self.company_id.id,
            'location_src_id': self.location_src_id.id,
            'location_dest_id': self.location_dest_id.id
        }
        for line in self.lines_id:
            data['product_id'] = line.product_id.id
            data['product_qty'] = line.product_qty
            data['product_uom_id'] = line.product_uom_id.id
            data['bom_id'] = line.bom_id.id
            data['routing_id'] = line.routing_id.id
            data['name'] = self.env['ir.sequence'].next_by_code('mrp.production')
            cr_mp = mp.create(data)


class MrpProductionBulkLine(models.TransientModel):
    _name = 'mrp.production.bulk.line'

    product_id = fields.Many2one('product.product', 'Produk')
    product_qty = fields.Float('Qty')
    product_uom_id = fields.Many2one('product.uom', 'UoM', compute='compute_product_uom_id')
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material')
    routing_id = fields.Many2one('mrp.routing', 'Routing', compute='_compute_routing')
    line_id = fields.Many2one('mrp.production.bulk')
    bom_related = fields.Many2many('mrp.bom', 'BoM related', compute='load_bom_related')
    wo_user_id = fields.Many2one('res.users', string='Operator')

    @api.multi
    @api.depends('bom_id.routing_id', 'bom_id.routing_id.operation_ids')
    def _compute_routing(self):
        for production in self:
            if production.bom_id.routing_id.operation_ids:
                production.routing_id = production.bom_id.routing_id.id
            else:
                production.routing_id = False

    def compute_product_uom_id(self):
        for rec in self:
            rec.product_uom_id = rec.product_id.product_tmpl_id.uom_id

    def get_bom_related(self):
        for rec in self:
            domain = [('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)]
            filtered_data = self.env['mrp.bom'].search(domain)
            filtered_list = filtered_data.mapped('id')
            return filtered_list

    @api.multi
    @api.depends('product_id')
    def load_bom_related(self):
        for rec in self:
            rec.bom_related = [(6, 0, rec.get_bom_related())]

    @api.onchange('product_id')
    def onchange_bom_id(self):
        for rec in self:
            res = {}
            bom_ids = rec.get_bom_related()
            if not bom_ids:
                res['domain'] = {'bom_related': []}
            else:
                rec.bom_id = bom_ids[0]
                res['domain'] = {'bom_related': [('id', 'in', rec.get_bom_related())]}
            return res
