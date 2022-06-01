# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
from . import popup_message
import logging
import datetime
from . import util
_rq = util.util.request
_popup = popup_message.popup_message
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    nxt_sync = fields.Selection(string="Estado de sincronización",selection=[("S","Sincronizado"),("N","No sincronizado"),("E","Error de sincronizacion")],default="N")
    nxt_id_erp = fields.Char('Código ERP')

    def synchronize_customer(self, company_id = None):
        for record in self:
            #if record.nxt_sync == "E":
            #    return True

            if not company_id:
                company_id = self.env.company.id

            data_obj = record.env["nextconnector.template_data"].search([('code','=','set_customer'),('state','=',True),('company_id','=',company_id)], limit=1)
            
            if data_obj.state != True: 
                return True

            results_vars = {}
            exec(data_obj.template_content, {"record":record,"env":self.env, "_logger":_logger},results_vars)

            response = _rq(self,"/nextconnector/api/records/customer",results_vars["json_data"],"post", record.company_id.id)

            if response["status_code"] != "200":
                self.write({"nxt_sync":'E'})
                self.message_post(body="Error de comunicación al sincronizar registro")
            else:
                json_resp = response["response_json"]
                if json_resp["code"] != "0":
                    self.write({"nxt_sync":'E'})
                    self.message_post(body=json_resp["message"])
                else:
                    if record.nxt_sync != 'S' or  record.nxt_id_erp != json_resp["id_erp"]:
                        record.write({"nxt_sync":'S', "nxt_id_erp":json_resp["id_erp"]})
                        self.message_post(body="Registro sincronizado con ERP.")
    
    def post_customer(self, params, company_id = None):
        
        if not company_id:
            company_id = self.env.company.id

        data_obj = self.env["nextconnector.template_query"].search([('code','=',"data_customer"),('state','=',True),('company_id','=',company_id) ], limit=1)
        if not data_obj: 
            return True

        results_vars = {}
        exec(data_obj.template_content, {"env":self.env, "record": params , "_logger":_logger},results_vars)

        response = _rq(self,"/nextconnector/api/records/customer",results_vars["json_data"],"get", company_id)

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
                            data_obj = self.env["nextconnector.template_query"].search([('code','=',"normalize_data_customer"),('state','=',True),('company_id','=',company_id) ], limit=1)
                            if data_obj.state != True: 
                                    return True

                            results_vars = {}
                            exec(data_obj.template_content, {"env":self.env, "record": row , "_logger":_logger},results_vars)

                            _logger.error("INFO POST :" + str(results_vars["json_data"]))
                            
                        except Exception as e:
                            _logger.info("Error al crear cliente :" + str(e))
                            raise Warning("Error al crear cliente :" + str(e))
    
    def get_customer_balance(self, company_id = None):

        for record in self:
            
            if not company_id:
                company_id = self.env.company.id

            data_obj = self.env["nextconnector.template_query"].search([('code','=',"data_customer_balance"),('state','=',True),('company_id','=',company_id) ], limit=1)
            if not data_obj: 
                return True

            results_vars = {}
            exec(data_obj.template_content, {"env":self.env, "record": record, "_logger":_logger},results_vars)

            response = _rq(self,"/nextconnector/api/records/customer",results_vars["json_data"],"get", company_id)

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
                                data_obj = self.env["nextconnector.template_query"].search([('code','=',"normalize_data_customer_balance"),('state','=',True),('company_id','=',company_id) ], limit=1)
                                if data_obj.state != True: 
                                        return True

                                results_vars = {}
                                exec(data_obj.template_content, {"env":self.env, "record": row , "_logger":_logger},results_vars)

                                _logger.error("INFO POST :" + str(results_vars["json_data"]))
                                #rec.action_done()
                                return _popup.success(self, "Importacion de datos de balance culminada.")
                            except Exception as e:
                                _logger.info("Error al consultar balance de cliente :" + str(e))
                                raise Warning("Error al consultar balance de cliente :" + str(e))
    

    """
    @api.model
    def create(self, vals_list):
        # CREATE OR UPDATE RECORD QUEUE 
        #self.write_record_queue(vals)
        return super(ResPartner, self).create(vals_list)

    @api.model
    def write(self, vals):
        #self.write_record_queue(vals)  
    return super(ResPartner, self).write(vals)"""
    
    
    def write_record_queue(self):
        for record_partner in self:
            rec = record_partner
            if record_partner.parent_id:
                rec = record_partner.parent_id
            record_queue = self.env["nextconnector.process_queue"].sudo().search([('model','=',rec._name),('record_id','=',rec.id)], limit=1)
            model_id = self.env["ir.model"].sudo().search([('model','=',rec._name)], limit=1)
            if record_queue: 
                record_queue.write({
                    "model_id":model_id.id
                    , "record_id":rec.id
                    , "name":rec.name
                    , "last_write_queue": datetime.datetime.now()
                    , "nxt_id_erp":rec.nxt_id_erp
                    , "nxt_sync": "N"
                })
            else:
                self.env['nextconnector.process_queue'].sudo().create({
                    "model_id":model_id.id
                    , "record_id":rec.id
                    , "name":rec.name
                    , "last_write_queue": datetime.datetime.now()
                    , "nxt_id_erp":rec.nxt_id_erp
                    , "nxt_sync": "N"
                    , "count_sync": 0
                }) 
