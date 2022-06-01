# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tarifa_despacho_id = fields.Many2one('dc.tarifa.despacho', string='Tarifa de despacho')
    costo_envio = fields.Float('Costo de envio')

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    razon_social_factura = fields.Char("Razón Social" )
    ruc_factura = fields.Char("RUC" )
    direccion_fiscal = fields.Char("Dirección Fiscal" )

    nombre_courier_cliente = fields.Char(string="Nombre del Courier")
    direccion_courier_cliente = fields.Char(string="Direccion de Agencia de Retiro")
    numero_documento_cliente = fields.Char(string="Número de documento")
    numero_contacto_cliente = fields.Char(string="Número de contacto")
    nombre_contacto_cliente = fields.Char(string="Nombre de contacto")
    
    # campo relacionado con agencias de envio
    agencia_envio = fields.Many2one('shipping.agencies', string='Agencia de Envío')
    
    # campo para el tipo de envio de agencia
    tipo_envio_agencia = fields.Selection(string="Tipo de envío de Agencia",selection=[
        ("agencia","Retira en Agencia"),
        ("direccion","Envío a dirección del cliente")
        ]
    ,default="direccion")


    lead_time_despacho = fields.Boolean('Lead Despacho', compute='_compute_lead_time_despacho')

    def _compute_lead_time_despacho(self):
        for record in self:
            
            min_lead_time = 2
            distrito = False 
            if record.partner_shipping_id.l10n_pe_district:
                distrito = record.partner_shipping_id.l10n_pe_district
            if (not record.website_id.is_site_b2b and distrito 
                and (not record.carrier_id.retiro_en_tienda and not record.carrier_id.envio_por_courier)): 
                lead_time = []
                for line in record.order_line:
                    if line.product_id.type == "product":
                        tarifa_despacho = self.env['dc.tarifa.despacho'].sudo().search([
                            ("district_id","=",distrito.id) ,
                            ("warehouse_id","in",line.sol_warehouse_id.id) ,
                        ], limit = 1)
                        lead_time.append(int(tarifa_despacho.lead_time))
                _logger.info("lead_time_despacho lead_time :" + str(lead_time))
                if lead_time:
                    min_lead_time = int(max(lead_time))   
                _logger.info("min_lead_time lead_time :" + str(min_lead_time))
            record.lead_time_despacho = min_lead_time

    def get_lead_time_despacho(self):
        for record in self:
            min_lead_time = 2
            distrito = False 
            if record.partner_shipping_id.l10n_pe_district:
                distrito = record.partner_shipping_id.l10n_pe_district
            if (not record.website_id.is_site_b2b and distrito 
                and (not record.carrier_id.retiro_en_tienda and not record.carrier_id.envio_por_courier)): 
                lead_time = []
                for line in record.order_line:
                    if line.product_id.type == "product":
                        tarifa_despacho = self.env['dc.tarifa.despacho'].sudo().search([
                            ("district_id","=",distrito.id) ,
                            ("warehouse_id","in",line.sol_warehouse_id.id) ,
                        ], limit = 1)
                        lead_time.append(int(tarifa_despacho.lead_time))
                _logger.info("lead_time_despacho lead_time :" + str(lead_time))
                if lead_time:
                    min_lead_time = int(max(lead_time))   
                _logger.info("min_lead_time lead_time :" + str(min_lead_time))
            return min_lead_time