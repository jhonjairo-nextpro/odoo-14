# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class CategoryInitials(models.Model):
    _name = 'category.initials'
    _description = 'category initials'

    name = fields.Char('Iniciales de Categoría')


class ProductInitials(models.Model):
    _name = 'product.initials'
    _description = 'product initials'

    name = fields.Char('Iniciales del Producto')


class ConventionalOrganic(models.Model):
    _name = 'conventional.organic'
    _description = 'conventional organic'

    name = fields.Char('Convencional / Orgánico')


class Correlativelote(models.Model):
    _name = 'correlative.lote'
    _description = "correlative lote"

    name = fields.Many2one('res.partner', string=('Proveedor'))
    correlative_lote = fields.Char('Correlativo de lote')
    correlative_seq = fields.Char('Secuencia', default='000-1')
    product_template = fields.Many2one('product.template')

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.correlative_lote = self.product_template.product_initials.name + \
                self.product_template.conventional_organic.name + self.name.code_client_provider


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_initials = fields.Many2one('product.initials', string='Iniciales del Producto')
    category_initials = fields.Many2one('category.initials', string='Iniciales de Categoría')
    conventional_organic = fields.Many2one('conventional.organic', string='Convencional / Orgánico')
    correlative = fields.Char('correlativo')
    correlative_lote_seq = fields.One2many('correlative.lote', 'product_template')
    correlative_lote = fields.Char('Correlativo de lote', default='000-1')

    @api.model
    def create(self, vals):
        if vals.get('conventional_organic', False) and vals.get('product_initials', False) and vals.get('category_initials', False) and not vals.get('correlative', False):
            correlative = self._get_next_code_product_barcode()
            vals['correlative'] = correlative
        res = super(ProductTemplate, self).create(vals)
        if res:
            if res.conventional_organic and res.product_initials and res.category_initials and res.correlative:
                res.default_code = (res.category_initials.name + '-' + res.product_initials.name +
                                    res.conventional_organic.name + '-' + res.correlative)
                res.barcode = res.default_code
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if self.conventional_organic and self.product_initials and self.category_initials and not self.correlative:
            correlative = self._get_next_code_product_barcode()
            code = (self.category_initials.name + '-' + self.product_initials.name +
                    self.conventional_organic.name + '-' + correlative)
            self.write({'default_code': code, 'barcode': code, 'correlative': correlative})
        return res

    def _get_next_code_product_barcode(self):
        return self.env['ir.sequence'].next_by_code('code.product_barcode')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    observation = fields.Text('observación')

    def action_generate_serial(self):
        self.ensure_one()
        self.lot_producing_id = self.env['stock.production.lot'].create({
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'mrp_production_ids': self.id
        })
        if self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids:
            self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids.lot_id = self.lot_producing_id
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()

    def write(self, vals):
        if self.id:
            if 'lot_producing_id' in vals:
                stock_production = self.env['stock.production.lot'].search([('id', '=',  vals['lot_producing_id'])])

                if self.move_raw_ids and self.lot_producing_id and self.move_byproduct_ids:
                    if self.move_raw_ids[0].lot_ids.display_name != stock_production.display_name:
                        vals['observation'] = 'Nombre de los lotes no son iguales'
                    else:
                        if self.move_raw_ids[0].lot_ids.display_name != self.move_byproduct_ids[0].lot_ids.name:
                            vals['observation'] = 'Nombre de los lotes no son iguales'
                        else:
                            if stock_production.display_name != self.move_raw_ids[0].lot_ids.display_name:
                                vals['observation'] = 'Nombre de los lotes no son iguales'
                            else:
                                if stock_production.display_name != self.move_byproduct_ids[0].lot_ids.name:
                                    vals['observation'] = 'Nombre de los lotes no son iguales'
                                else:
                                    if self.move_byproduct_ids[0].lot_ids.name != self.move_raw_ids[0].lot_ids.display_name:
                                        vals['observation'] = 'Nombre de los lotes no son iguales'
                                    else:
                                        if self.move_byproduct_ids[0].lot_ids.name != stock_production.display_name:
                                            vals['observation'] = 'Nombre de los lotes no son iguales'
                                        else:
                                            vals['observation'] = False
        return super(MrpProduction, self).write(vals)


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    mrp_production_ids = fields.Many2one('mrp.production')
    order_id = fields.Many2one('sale.order', 'Used in')
    order_id_purchase = fields.Many2one('purchase.order', 'purchase')

    @api.model_create_multi
    def create(self, vals_list):
        obj_Production = self.search([])
        if 'default_product_id' in self.env.context:
            product_id = self.product_id.search([('id', '=', self.env.context['default_product_id'])])
        if 'active_picking_id' in self.env.context:
            if self.env.context['active_picking_id']:
                for vals_list_id in vals_list:
                    stock_piking = self.env['stock.picking'].search([('id', '=', self.env.context['active_picking_id'])])
                    if stock_piking:
                        if stock_piking.partner_id.parent_id:
                            provider = stock_piking.partner_id.parent_id.code_client_provider
                        else:
                            provider = stock_piking.partner_id.code_client_provider
                    else:
                        provider = 'P'
                    next = product_id.correlative_lote.split('-')
                    name = (product_id.product_initials.name + product_id.conventional_organic.name + provider +
                            next[0] + next[1])
                    correlative_lote = int(next[1]) + 1
                    product_id.correlative_lote = next[0] + '-' + str(correlative_lote)
                    vals_list_id['name'] = name
        if 'default_order_id_purchase' in self.env.context:
            for vals_list_id in vals_list:
                order_id_purchase = self.env['purchase.order'].search([('id', '=', self.env.context['default_order_id_purchase'])])
                _logger.info(f"""
                
                

                {self.env.context}
                {product_id}
                {product_id.product_initials}
                {product_id.product_initials.name}
                {product_id.conventional_organic}
                {product_id.conventional_organic.name}
                {order_id_purchase}
                {order_id_purchase.partner_id.code_client_provider}
                {order_id_purchase.partner_id.code_client_provider}
                
                

                """)
                correlative = product_id.product_initials.name + product_id.conventional_organic.name + order_id_purchase.partner_id.code_client_provider
                correlative_lote_seq = product_id.correlative_lote_seq.filtered(
                    lambda c: c.name == order_id_purchase.partner_id) if product_id.correlative_lote_seq else False
                if correlative_lote_seq:
                    correlative_lote_product = correlative_lote_seq
                else:
                    vals = {
                        'name': order_id_purchase.partner_id.id,
                        'correlative_lote': correlative,
                        'product_template': product_id.product_tmpl_id.id
                    }
                    correlative_lote_product = self.correlative_lote(vals)
                next = correlative_lote_product.correlative_seq.split('-')
                name = (correlative + next[0] + next[1])
                c = 1
                lote = obj_Production.filtered(
                    lambda lot: lot.name == name and lot.product_id == product_id)
                if lote:
                    for p in range(int(next[1])+1, len(obj_Production)):
                        name = (correlative + next[0] + str(p))
                        lote = obj_Production.filtered(
                            lambda lot: lot.name == name and lot.product_id == product_id)
                        if not lote:
                            c = p
                            break
                if c > 1:
                    correlative_lote = c
                else:
                    correlative_lote = int(next[1]) + c
                correlative_lote_product.correlative_seq = next[0] + '-' + str(correlative_lote)
                vals_list_id['name'] = name
        Production = super(ProductionLot, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
        list = []
        if Production:
            for Lot in Production:
                if Lot.mrp_production_ids:
                    for move_raw_ids in Lot.mrp_production_ids.move_raw_ids:
                        if move_raw_ids.move_line_ids.lot_id:
                            list.append(move_raw_ids.move_line_ids.lot_id.name)
                    if len(list) == 1:
                        lote = obj_Production.filtered(
                            lambda line: line.product_id == Lot.mrp_production_ids.product_id and
                            line.name in list[0])
                        if not lote:
                            Lot.name = list[0]
                        else:
                            Lot.mrp_production_ids.observation = 'Lote ya existe con el mismo producto y mismo nombre del lote de la linea  / Se creo el lote de forma automatica'
                    else:
                        if len(list) == 0:
                            Lot.mrp_production_ids.observation = 'Las lineas no posee ningun lote '
                        else:
                            Lot.mrp_production_ids.observation = 'las lineas poseen mas de un lote / Se creo el lote de forma automatica'
        return Production

    def correlative_lote(self, vals):
        correlative_lote_obj = self.env['correlative.lote']
        correlative_lote_product = correlative_lote_obj.sudo().create(vals)
        correlative_lote_product._cr.commit()
        return correlative_lote_product


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', copy=False)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', copy=False)
    lot_id_block = fields.Boolean('', default=True, compute='_onchange_product_kiria')

    @api.onchange('product_id')
    def _onchange_product_kiria(self):
        for line in self:
            if line.product_id.product_initials.name:
                line.lot_id_block = False
            else:
                line.lot_id_block = True


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.onchange('location_dest_id')
    def _onchange_location_dest_id_lote(self):
        if 'default_picking_id' in self.env.context:
            stock_piking = self.env['stock.picking'].search([('id', '=', self.env.context['default_picking_id'])])
            if stock_piking and stock_piking.purchase_id:
                stock_production_lot = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id),
                                                                               ('order_id_purchase', '=', stock_piking.purchase_id.id),
                                                                                ('name', '=', self.move_id.lot_id_oc)])
                if stock_production_lot:
                    self.lot_id = stock_production_lot.id
        else:
            self.location_dest_id = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_id_oc = fields.Char('Lot/Serial Number OC', copy=False, compute='_compute_lot_id_oc')

    def _compute_lot_id_oc(self):
        self.lot_id_oc = 'Vacio'
        if self:
            if self.picking_id.purchase_id:
                for move in self:
                    move.lot_id_oc = move.purchase_line_id.lot_id.name
            else:
                self.lot_id_oc = 'Vacio'
