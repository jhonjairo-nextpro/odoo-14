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

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nxt_sync = fields.Selection(string="Estado de sincronización",selection=[("S","Sincronizado"),("N","No sincronizado"),("E","Error de sincronizacion")],default="N")
    nxt_id_erp = fields.Char('Código ERP')

    def synchronize_record(self):
        for record in self:
            #for rec in self:
            if record.nxt_sync == "S":
                return 

            data_obj = record.env["nextconnector.template_data"].search([('code','=','set_sale_order'),('company_id','=',record.company_id.id)], limit=1)
            if data_obj.state != True: 
                return 

            results_vars = {}
            exec(data_obj.template_content, {"record":record,"env":self.env, "_logger":_logger},results_vars)

            response = _rq(self,"/nextconnector/api/records/transaction",results_vars["json_data"],"post", record.company_id.id)

            if response["status_code"] != "200":
                record.message_post(body="Error de comunicación al sincronizar registro")
            else:
                json_resp = response["response_json"]
                if json_resp["code"] != "0":
                    record.message_post(body=json_resp["message"])
                else:
                    record.write({"nxt_sync":'S', "nxt_id_erp":json_resp["id_erp"]})
                    record.message_post(body="Registro sincronizado con ERP")
                

    #COPY FROM partner_credit_limit
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.user_type_id.name', 'in',
                  ['Receivable', 'Payable'])]
            )
            confirm_sale_order = self.search([('partner_id', '=', partner.id),
                                              ('state', '=', 'sale')])
            debit, credit = 0.0, 0.0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for line in movelines:
                credit += line.credit
                debit += line.debit
            partner_credit_limit = (partner.credit_limit - debit) + credit
            available_credit_limit = \
                ((partner_credit_limit -
                  (amount_total - debit)) + self.amount_total)

            if (amount_total - debit) > partner_credit_limit:
                if not partner.over_credit:
                    msg = ' Crédito insuficiente, ' \
                          ' monto otorgado: = %s \n' \
                           % (available_credit_limit)
                    raise UserError('No es posible confimar la orden de venta . \n' + msg)
                partner.write(
                    {'credit_limit': credit - debit + self.amount_total})
            return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        #for order in self:
            #order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            return True # por pruebas
            order.check_limit()

    # Onchange para codigo del cliente
    
    #@api.onchange('partner_id')
    def onchange_customer(self):
        if self.partner_id:
 
            query =  """SELECT  T1."Balance" AS "nxt_balance",  T1."CreditLine" AS "credit_limit" 
                        FROM "OCRD" T1 
                        WHERE T1."CardType" IN ('C','L') AND T1."LicTradNum" = '{id}' """.format(id=self.partner_id.vat)

            record = {
                "id": "",
                "record_type": "item",
                "fields": [
                        {"name": "query","value": query}
                    ]
            }

            response = _rq(self,"/nextconnector/api/records/customers",record,"get")

            if response["status_code"] != "200":
                return _popup.error(self, "Error de comunicación")
            else:
                json_resp = response["response_json"]
                if json_resp["code"] != "0":
                    return _popup.error(self, json_resp["message"])
                else:
                    for list_data in json_resp["list_data"] :
                        for row in list_data["data"] :
                            try:
                                rec = self.env['res.partner'].search([('vat','=',self.partner_id.vat)])
                                if rec :
                                    result = rec.write(row)
                                    _logger.info("Update cliente !  id:" + str(result) + " - " + str(row))
                                else:
                                    result = self.env['res.partner'].create(row)
                                    _logger.info("Create cliente !  id:" + str(result) + " - " + str(row))
                            except Exception as e:
                                _logger.info("Error al crear cliente :" + str(e))
                                raise Warning("Error al crear cliente :" + str(e))
        