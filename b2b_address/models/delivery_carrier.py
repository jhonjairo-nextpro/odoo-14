# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    warehouse_id = fields.Many2one('stock.warehouse', string='Almacen de despacho Principal', domain="[('company_id', 'in', [company_id,False])]")
    warehouse_allowed_ids = fields.Many2many('stock.warehouse', string="Almacen de despacho Secundarias", domain="[('company_id', 'in', [company_id,False])]")

    country_ids = fields.Many2many('res.country', 'delivery_carrier_country_rel', 'carrier_id', 'country_id', 'Pais', domain="[('code', '=', 'PE')]")
    state_ids = fields.Many2many('res.country.state', 'delivery_carrier_state_rel', 'carrier_id', 'state_id', 'Departamento', domain="[('country_id', 'in', country_ids)]")
    city_ids = fields.Many2many('res.city', 'delivery_carrier_city_rel', 'carrier_id', 'city_id', 'Provincia', domain="[('state_id', 'in', state_ids)]")
    district_ids = fields.Many2many('l10n_pe.res.city.district',string='Distrito', domain="[('city_id', 'in', city_ids)]")

    etiqueta_retiro_tienda = fields.Char('Etiqueta retiro en tienda')
    direccion_retiro_tienda = fields.Char('Direccion retiro en tienda')
    retiro_en_tienda = fields.Boolean('Retiro en tienda')
    envio_por_courier = fields.Boolean('Envio por Courier')

    precio_base_kg = fields.Float('Precio base 1 Kg')
    precio_kg_adicional = fields.Float('Precio Kg adicional')

    precio_base_kg_valorado = fields.Float('Precio base 1 Kg Valorado')
    precio_kg_adicional_valorado = fields.Float('Precio Kg adicional Valorado')
    
    state_id = fields.Many2one('res.country.state', string='Departamento Destino', domain="[('country_id', '=', 'PE')]")
    city_id = fields.Many2one('res.city', string='Provincia Destino', domain="[('state_id', '=', state_id)]")
    district_id = fields.Many2one('l10n_pe.res.city.district', string='Distrito Destino', domain="[('city_id', '=', city_id)]")

    

    dc_tarifa_despacho = fields.Many2many('dc.tarifa.despacho', "carrier_id", string="Origenes de despacho")

    precio_envio_por_agencia = fields.Float('Precio Envio por Agencia')
    amount_free_ship_envio_por_agencia = fields.Float('Monto Neto para envio gratis por Agencia')
    

    #SE SOBRE-ESCRIBE METODO DE METODOS DE ENVIO DISPONIBLE
    def _match_address(self, partner, order=None):
        self.ensure_one()
        _logger.error(" Entro self.name: " + str(self.name))
        if self.country_ids and partner.country_id not in self.country_ids:
            return False
        if self.state_ids and partner.state_id not in self.state_ids:
            return False
        if self.zip_from and (partner.zip or '').upper() < self.zip_from.upper():
            return False
        if self.zip_to and (partner.zip or '').upper() > self.zip_to.upper():
            return False
        if self.city_ids and partner.city_id not in self.city_ids:
            return False
        if self.district_ids and partner.l10n_pe_district not in self.district_ids:
            return False
        return True

    def available_carriers(self, partner):
        return self.filtered(lambda c: c._match_address(partner))

    def base_on_rule_rate_shipment(self, order):
        carrier = self._match_address(order.partner_shipping_id, order)
        if not carrier:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this delivery method is not available for this address.'),
                    'warning_message': False}

        try:
            price_unit = self._get_price_available(order)
        except UserError as e:
            return {'success': False,
                    'price': 0.0,
                    'error_message': e.name,
                    'warning_message': False}
        #if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
        #    price_unit = order.company_id.currency_id._convert(
        #        price_unit, order.pricelist_id.currency_id, order.company_id, order.date_order or fields.Date.today())

        _logger.error(" >>> base_on_rule_rate_shipment: " + str(price_unit))
        return {'success': True,
                'price': price_unit,
                'error_message': False,
                'warning_message': False}

    def _get_price_available(self, order):
        self.ensure_one()
        self = self.sudo()
        order = order.sudo()
        total = weight = volume = quantity = 0
        total_delivery = 0.0
        total_neto = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                total_delivery += line.price_total
            if not line.product_id or line.is_delivery:
                continue
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty
            quantity += qty
        total = (order.amount_total or 0.0) - total_delivery


        _logger.error(" Entro carrier: " + str(self))
        precio_base_kg = self.precio_base_kg
        precio_kg_adicional = self.precio_kg_adicional
        precio_base_kg_valorado = self.precio_base_kg_valorado
        precio_kg_adicional_valorado = self.precio_kg_adicional_valorado
        free_ship_amount_order = 0

        price_total = 0.0
        tarifa_despacho_ids = []
        tarifa_despacho_vals = []
        sum_lines_vals = []
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            #if self.retiro_en_tienda:
            #    break
            if not line.product_id or line.is_delivery:
                continue
            
            district = order.partner_shipping_id.l10n_pe_district
            if self.retiro_en_tienda:
                 district = self.district_id
            tarifa_despacho = None
            if district:
                tarifa_despacho = self.env['dc.tarifa.despacho'].sudo().search([
                    ("district_id","=",district.id) ,
                    ("warehouse_id","in",line.sol_warehouse_id.id) ,
                ], limit = 1)

            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight_line = (line.product_id.weight or 0.0)*qty
            price_unit = 0.0
            price_delivery_line = 0.0
            if qty > 0:
                price_unit = (line.price_total or 0.0) / qty
                total_neto = total_neto + (qty*line.price_unit)

            if order.pricelist_id.currency_id.name == "PEN":
                tipo_cambio = self.env['dc.tipo.cambio'].search([])
                _logger.info(" _get_price_available price_unit ========================== ")
                _logger.info(" _get_price_available price_unit: " + str(price_unit))
                price_unit = round(price_unit/tipo_cambio.tipo_cambio_compra,2)
                total_neto = round(total_neto/tipo_cambio.tipo_cambio_compra,2)
                _logger.info(" _get_price_available price_unit: " + str(price_unit))
            
            if tarifa_despacho and not line.is_delivery:
                flag_exist_tarifa_despacho = False
                if sum_lines_vals:
                    for sum_lines in sum_lines_vals:
                        if sum_lines["tarifa_despacho_id"] == tarifa_despacho.id:
                            sum_lines["weight"] += weight_line
                            sum_lines["total_neto"] += total_neto
                            flag_exist_tarifa_despacho = True
                            break
                        
                if not flag_exist_tarifa_despacho:
                    sum_lines_vals.append({
                        "tarifa_despacho_id": tarifa_despacho.id, 
                        "tarifa_despacho": tarifa_despacho, 
                        "weight": weight_line, 
                        "total_neto":total_neto,
                    })

            _logger.info(f" _get_price_available sum_lines_vals {sum_lines_vals}")
        
        for sum_lines in sum_lines_vals:
            tarifa_despacho = sum_lines["tarifa_despacho"]
            precio_base_kg = tarifa_despacho.precio_base_kg
            precio_kg_adicional = tarifa_despacho.precio_kg_adicional
            precio_base_kg_valorado = tarifa_despacho.precio_base_kg_valorado
            precio_kg_adicional_valorado = tarifa_despacho.precio_kg_adicional_valorado
            free_ship_amount_order = tarifa_despacho.free_ship_amount_order

            if sum_lines["total_neto"] <= 1000:
                if sum_lines["weight"] <= 1:
                    price_delivery_line = precio_base_kg
                else:
                    price_delivery_line = (precio_base_kg+(precio_kg_adicional*(sum_lines["weight"]-1)))
                _logger.info(" _get_price_available price_unit <= 1000: " + str(price_delivery_line))
            else:
                if sum_lines["weight"] <= 1:
                    price_delivery_line = precio_base_kg_valorado
                else:
                    price_delivery_line = (precio_base_kg_valorado+(precio_kg_adicional_valorado*(sum_lines["weight"]-1)))
                _logger.info(" _get_price_available price_unit > 1000: " + str(price_delivery_line))

            if tarifa_despacho.id not in tarifa_despacho_ids:
                tarifa_despacho_ids.append(tarifa_despacho.id)
            tarifa_despacho_vals.append({
                "warehouse_id": tarifa_despacho.warehouse_id.mapped('id'),
                "tarifa_despacho": tarifa_despacho.id,
                "costo_envio": price_delivery_line,
                "total_neto": total_neto,   
                "free_ship_amount_order": tarifa_despacho.free_ship_amount_order,                  
            })

            """ if not line.is_delivery:
                if price_unit <= 1000:
                    if weight_line <= 1:
                        price_delivery_line = precio_base_kg*qty
                    else:
                        price_delivery_line = (precio_base_kg+(precio_kg_adicional*(weight_line-1)))*qty
                    _logger.info(" _get_price_available price_unit <= 1000: " + str(price_delivery_line))
                else:
                    if weight_line <= 1:
                        price_delivery_line = precio_base_kg_valorado* qty
                    else:
                        price_delivery_line = (precio_base_kg_valorado+(precio_kg_adicional_valorado*(weight_line-1)))* qty
                    _logger.info(" _get_price_available price_unit > 1000: " + str(price_delivery_line))

                if tarifa_despacho:
                    _logger.info(" _get_price_available line.sol_warehouse_id: " + str(line.sol_warehouse_id.name))
                    line.write({
                        "tarifa_despacho_id": tarifa_despacho.id,
                        "costo_envio": price_delivery_line
                    })
                    if tarifa_despacho.id not in tarifa_despacho_ids:
                        tarifa_despacho_ids.append(tarifa_despacho.id)
                    tarifa_despacho_vals.append({
                        "warehouse_id": tarifa_despacho.warehouse_id.mapped('id'),
                        "tarifa_despacho": tarifa_despacho.id,
                        "costo_envio": price_delivery_line,
                        "total_neto": total_neto,   
                        "free_ship_amount_order": tarifa_despacho.free_ship_amount_order,                  
                    })
                """
                #price_total = price_total + price_delivery_line
                #_logger.info(" _get_price_available price_total: " + str(price_total))

        _logger.info(" _get_price_available tarifa_despacho_ids: " + str(tarifa_despacho_ids))
        _logger.info(" _get_price_available tarifa_despacho_vals: " + str(tarifa_despacho_vals))
        price_total = 0
        for tf_id in tarifa_despacho_ids:
            total_neto = 0 
            free_ship_amount_order = 0 
            costo_envio_tarifa = 0
            warehouse_id = 0
            for tf_val in tarifa_despacho_vals:
                if tf_val["tarifa_despacho"] == tf_id:
                    total_neto += tf_val["total_neto"]
                    free_ship_amount_order = tf_val["free_ship_amount_order"]
                    costo_envio_tarifa += tf_val["costo_envio"]
                    warehouse_id = tf_val["warehouse_id"]

            _logger.info(f" _get_price_available free_ship_amount_order:{free_ship_amount_order} - total_neto:{total_neto} -")
            if free_ship_amount_order > 0 and free_ship_amount_order <= total_neto and self.warehouse_id.id in warehouse_id:
                costo_envio_tarifa = 0
            
            if self.retiro_en_tienda and self.warehouse_id.id in warehouse_id:
                costo_envio_tarifa = 0

            price_total += costo_envio_tarifa

        #ENVIO POR AGENCIA
        if self.envio_por_courier:
            price_total = self.precio_envio_por_agencia
        if self.envio_por_courier and (order.amount_untaxed - order.amount_delivery)  >= self.amount_free_ship_envio_por_agencia :
            price_total = 0
        
            

        if order.pricelist_id.currency_id.name == "PEN":
            tipo_cambio = self.env['dc.tipo.cambio'].search([])
            price_total = round(price_total*tipo_cambio.tipo_cambio_venta,2)
            _logger.info(" _get_price_available tipo_cambio: " + str(tipo_cambio))
            _logger.info(" _get_price_available price_total: " + str(price_total))
            
        #if price_total > 0:
        return price_total
        #total = order.currency_id._convert(
        #    total, order.company_id.currency_id, order.company_id, order.date_order or fields.Date.today())

        return self._get_price_from_picking(total, weight, volume, quantity)



    def base_on_rule_send_shipping(self, pickings):
        res = []
        for p in pickings:
            carrier = self._match_address(p.partner_id, pickings)
            if not carrier:
                raise ValidationError(_('There is no matching delivery rule.'))
            res = res + [{'exact_price': p.carrier_id._get_price_available(p.sale_id) if p.sale_id else 0.0,  # TODO cleanme
                          'tracking_number': False}]
        return res

    def fixed_rate_shipment(self, order):
        self.ensure_one()
        self = self.sudo()
        order = order.sudo()

        carrier = self._match_address(order.partner_shipping_id, order)
        if not carrier:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this delivery method is not available for this address.'),
                    'warning_message': False}
        price = self.fixed_price
        
        _logger.error(" Entro carrier: " + str(self))
        precio_base_kg = self.precio_base_kg
        precio_kg_adicional = self.precio_kg_adicional

        precio_base_kg_valorado = self.precio_base_kg_valorado
        precio_kg_adicional_valorado = self.precio_kg_adicional_valorado
        free_ship_amount_order = 0
        total_neto = 0.0

        price_total = 0.0
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if self.retiro_en_tienda:
                break
            if not line.product_id or line.is_delivery:
                continue


            district = order.partner_shipping_id.l10n_pe_district
            if district:
                tarifa_despacho = self.env['dc.tarifa.despacho'].sudo().search([
                    ("district_id","=",district.id) ,
                    ("warehouse_id","in",line.sol_warehouse_id.id) ,
                ], limit = 1)
                _logger.info(" _get_price_available tarifa_despacho " + str(tarifa_despacho))
                if tarifa_despacho:
                    precio_base_kg = tarifa_despacho.precio_base_kg
                    precio_kg_adicional = tarifa_despacho.precio_kg_adicional
                    precio_base_kg_valorado = tarifa_despacho.precio_base_kg_valorado
                    precio_kg_adicional_valorado = tarifa_despacho.precio_kg_adicional_valorado
                    free_ship_amount_order = tarifa_despacho.free_ship_amount_order
                    
            qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
            weight_line = (line.product_id.weight or 0.0)
            price_unit = 0.0
            price_delivery_line = 0.0
            if qty > 0:
                price_unit = (line.price_total or 0.0) / qty
                total_neto = total_neto + (qty*line.price_unit)
        
            if order.pricelist_id.currency_id.name == "PEN":
                tipo_cambio = self.env['dc.tipo.cambio'].search([])
                price_unit = round(price_unit/tipo_cambio.tipo_cambio_compra,2)
                total_neto = round(total_neto/tipo_cambio.tipo_cambio_compra,2)

            if not line.is_delivery:
                if price_unit <= 1000:
                    if weight_line <= 1:
                        price_delivery_line = precio_base_kg*qty
                    else:
                        price_delivery_line = (precio_base_kg+(precio_kg_adicional*(weight_line-1)))*qty
                    _logger.info(" fixed_rate_shipment price_unit <= 1000: " + str(price_delivery_line))
                else:
                    if weight_line <= 1:
                        price_delivery_line = precio_base_kg_valorado* qty
                    else:
                        price_delivery_line = (precio_base_kg_valorado+(precio_kg_adicional_valorado*(weight_line-1)))* qty
                    _logger.info(" fixed_rate_shipment price_unit > 1000: " + str(price_delivery_line))

                price_total = price_total + price_delivery_line
                _logger.info(" fixed_rate_shipment price_total: " + str(price_total))
        
        _logger.info(" fixed_rate_shipment free_ship_amount_order: " + str(free_ship_amount_order))
        _logger.info(" fixed_rate_shipment total_neto: " + str(total_neto))
        if free_ship_amount_order > 0 and free_ship_amount_order <= total_neto:
            price_total = 0

        if order.pricelist_id.currency_id.name == "PEN":
            tipo_cambio = self.env['dc.tipo.cambio'].search([])
            price_total = round(price_total/tipo_cambio.tipo_cambio_compra,2)

        if price_total > 0:
            return price_total

        _logger.info(" fixed_rate_shipment price_total: " + str(price_total))
        company = self.company_id or order.company_id or self.env.company
        if company.currency_id and company.currency_id != order.currency_id:
            price = company.currency_id._convert(price, order.currency_id, company, fields.Date.today())
        
        _logger.info(" fixed_rate_shipment _convert price: " + str(price))
        return {'success': True,
                'price': price,
                'error_message': False,
                'warning_message': False}

class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    @api.depends('partner_id')
    def _compute_available_carrier(self):
        _logger.error(" Entro DeliveryCarrier _compute_available_carrier: " + str(self))
        for rec in self:
            carriers = self.env['delivery.carrier'].search(['|', ('company_id', '=', False), ('company_id', '=', rec.order_id.company_id.id)])
            rec.available_carrier_ids = carriers.available_carriers(rec.order_id.partner_shipping_id, rec.order_id) if rec.partner_id else carriers

