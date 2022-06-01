# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
import logging
from . import popup_message
from . import util
_rq = util.util.request

_logger = logging.getLogger(__name__)
_popup = popup_message.popup_message

class ProcessQueue(models.Model):
    _name = 'nextconnector.process_queue'
    _description = 'Cola de sincronización de registros'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    model_id = fields.Many2one('ir.model', 'Modelo to',)
    model = fields.Char('Modelo relacionado', related='model_id.model', index=True, store=True, readonly=True)
    record_id = fields.Char('ID de registro', index=True)
    name = fields.Char('Nombre de registro')
    last_write_queue = fields.Datetime(string="Fecha ultimo registro en cola")
    last_sync = fields.Datetime(string="Fecha ultimo intento")
    count_sync = fields.Integer(string="Numero de intentos")
    url_request = fields.Char('URL request')
    json_request = fields.Char('JSON request')
    json_response = fields.Char('JSON response')
    message_sync = fields.Char('Mensaje de syncronización')
    nxt_id_erp = fields.Char('Código ERP')
    nxt_sync = fields.Selection(string="Estado de sincronización",selection=[("S","Sincronizado"),("N","No sincronizado"),("E","Error de sincronizacion")],default="N")

