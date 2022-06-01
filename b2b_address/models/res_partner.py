# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_default_address = fields.Boolean("Dirección por defecto?" )
    is_default_contact = fields.Boolean("Contacto por defecto?" )

    razon_social_factura = fields.Char("Razón Social" )
    ruc_factura = fields.Char("RUC" )
    direccion_fiscal = fields.Char("Dirección Fiscal" )

    primer_nombre = fields.Char("Primer Nombre")
    segundo_nombre = fields.Char("Segundo Nombre")
    
    tipo_persona = fields.Selection(string="Tipo de persona",selection=[
        ("natural","Natural"),
        ("empresa","Empresa")
        ]
    ,default="natural")

    tipo_identificacion = fields.Selection(string="Tipo de identificacion",selection=[
        ("1","DNI"),
        ("4","CARNET DE EXTRAJERIA"),
        ("6","RUC"),
        ("7","PASAPORTE")
        ]
    )

    tipo_documento = fields.Selection(string="Tipo de documento",selection=[
        ("boleta","Boleta"),
        ("factura","Factura")
        ]
    ,default="boleta")

    address_format_custom = fields.Char(compute='_compute_address_format_custom')

    def _compute_address_format_custom(self):
        for contac in self:
            address_format_custom = "" if not contac.street else contac.street
            address_format_custom += ", " if not contac.l10n_pe_district else ", "  + contac.l10n_pe_district.name 
            address_format_custom += ", " if not contac.city_id else ", "  + contac.city_id.name 
            address_format_custom += ", " if not contac.state_id else ", "  + contac.state_id.name 
            contac.address_format_custom = address_format_custom

    # Peruvian VAT validation, contributed by Vauxoo
    def check_vat_pe(self, vat):
        """if len(vat) != 11 or not vat.isdigit():
            return False
        dig_check = 11 - (sum([int('5432765432'[f]) * int(vat[f]) for f in range(0, 10)]) % 11)
        if dig_check == 10:
            dig_check = 0
        elif dig_check == 11:
            dig_check = 1
        return int(vat[10]) == dig_check"""
        return True