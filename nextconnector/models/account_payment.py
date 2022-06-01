# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
from odoo.exceptions import UserError
from . import popup_message
import logging
from . import util
from datetime import date
import locale

_rq = util.util.request
_popup = popup_message.popup_message
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.payment'

    nxt_sync = fields.Selection(string="Estado de sincronización",selection=[("S","Sincronizado"),("N","No soncronizado"),("E","Error de sincronizacion")],default="N")
    nxt_id_erp = fields.Char('Código ERP')
    nxt_payment_ref = fields.Char('Referencia de pago')

    def synchronize_record(self):

        for record in self:
            if record.nxt_sync == "S":
                return True
            
            data_obj = record.env["nextconnector.template_data"].search([('code','=','set_payment'),('company_id','=',record.company_id.id)], limit=1)
            if data_obj.state != True: 
                return True

            results_vars = {}
            exec(data_obj.template_content, {"record":record,"env":self.env, "_logger":_logger},results_vars)

            response = _rq(self,"/nextconnector/api/records/payment",results_vars["json_data"],"post", record.company_id.id)

            if response["status_code"] != "200":
                self.message_post(body="Error de comunicación al sincronizar registro")
            else:
                json_resp = response["response_json"]
                if json_resp["code"] != "0":
                    self.message_post(body=json_resp["message"])
                else:
                    self.write({"nxt_sync":'S', "nxt_id_erp":json_resp["id_erp"]})
                    self.message_post(body="Registro sincronizado con ERP")
