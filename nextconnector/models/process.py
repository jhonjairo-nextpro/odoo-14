# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from . import popup_message
from . import util
from . import product_template as _product
from . import product_pricelist as _pricelist
from . import res_partner as _customer
import requests
import json 
import logging
_logger = logging.getLogger(__name__)
_rq = util.util.request
_popup = popup_message.popup_message

class Process(models.TransientModel):
    _name="nextconnector.process"
    _description = "Procesos generales del conector"

    def import_items(self, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        data_obj = self.env["nextconnector.template_query"].search([('code','=',"list_products"),('state','=',True),('company_id','=',company_id) ], limit=1)
        if data_obj.state != True: 
                return True

        results_vars = {}
        exec(data_obj.template_content, {"env":self.env, "_logger":_logger},results_vars)

        response = _rq(self,"/nextconnector/api/records/items",results_vars["json_data"],"get", company_id)

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                return _popup.error(self, json_resp["message"])
            else:
                for list_data in json_resp["list_data"] :
                    #for rec in self.web_progress_iter(data, msg="Importando articulos") :
                    for row in list_data["data"] :
                        _product.ProductTemplate.post_product(self, row, company_id)

                return _popup.success(self, "Importación culminada.")
                
    def import_customers(self, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        data_obj = self.env["nextconnector.template_query"].search([('code','=',"list_customers"),('state','=',True),('company_id','=',company_id) ], limit=1)
        if not data_obj: 
            return True

        results_vars = {}
        exec(data_obj.template_content, {"env":self.env, "_logger":_logger},results_vars)

        response = _rq(self,"/nextconnector/api/records/customers",results_vars["json_data"],"get", company_id)

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                return _popup.error(self, json_resp["message"])
            else:
                for list_data in json_resp["list_data"] :
                    #for rec in self.web_progress_iter(data, msg="Importando Clientes") :
                    for row in list_data["data"] :
                        _customer.ResPartner.post_customer(self, row, company_id)

                return _popup.success(self, "Importación culminada.")

    def import_stock_inventory(self, company_id = None):
        
        if not company_id:
            company_id = self.env.company.id

        data_obj = self.env["nextconnector.template_query"].search([('code','=',"stock_products"),('state','=',True),('company_id','=',company_id) ], limit=1)
        if not data_obj: 
            return True

        results_vars = {}
        exec(data_obj.template_content, {"env":self.env, "_logger":_logger},results_vars)

        response = _rq(self,"/nextconnector/api/records/items",results_vars["json_data"],"get", company_id)

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                return _popup.error(self, json_resp["message"])
            else:
                for list_data in json_resp["list_data"] :        
                    try:
                        data_obj = self.env["nextconnector.template_query"].search([('code','=',"normalize_stock_products"),('state','=',True),('company_id','=',company_id) ], limit=1)
                        if data_obj.state != True: 
                                return True

                        results_vars = {}
                        exec(data_obj.template_content, {"env":self.env, "record": list_data , "_logger":_logger},results_vars)

                        _logger.error("INFO POST :" + str(results_vars["json_data"]))
                        #rec.action_done()
                        return _popup.success(self, "Importación culminada.")
                    except Exception as e:
                        _logger.info("Error al crear ajuste de inventario :" + str(e))
                        raise Warning("Error al crear ajusre de inventario :" + str(e))
    
    def import_product_pricelist(self, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        data_obj = self.env["nextconnector.template_query"].search([('code','=',"list_product_pricelist"),('state','=',True),('company_id','=',company_id) ], limit=1)
        if data_obj.state != True: 
                return True

        results_vars = {}
        exec(data_obj.template_content, {"env":self.env, "_logger":_logger},results_vars)

        response = _rq(self,"/nextconnector/api/records/items",results_vars["json_data"],"get", company_id)

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                return _popup.error(self, json_resp["message"])
            else:
                for list_data in json_resp["list_data"] :
                    for row in list_data["data"] :
                        _pricelist.ProductPriceList.post_product_pricelist(self, row, company_id)

                return _popup.success(self, "Importación culminada.")

    def get_data_query(self, query_string="", company_id = None):

        if not company_id:
            company_id = self.env.company.id

        if not query_string: 
                return True

        record = {
            "id": "",
            "record_type": "get_data_query",
            "fields": [
                    {"name": "query","value": query_string}
                ]
        }

        response = _rq(self,"/nextconnector/api/records/items",record,"get", company_id)

        if response["status_code"] != "200":
            return None
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                return None
            else:
                for list_data in json_resp["list_data"] :
                    if list_data["data"]:
                        return list_data["data"]
        return None

    def post_generic_request(self, record, url_route, template_data_code, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        if not url_route or not template_data_code: 
                return True

        data_obj = self.env["nextconnector.template_data"].search([('code','=',template_data_code),('state','=',True),('company_id','=',company_id)], limit=1)
        if data_obj.state != True: 
            return 

        results_vars = {}
        exec(data_obj.template_content, {"record":record,"env":self.env, "_logger":_logger},results_vars)

        response = _rq(self,url_route,results_vars["json_data"],"post", company_id)

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            return json_resp

    def exec_template_code(self, record, template_data_code, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        if not template_data_code: 
                return True

        data_obj = self.env["nextconnector.template_data"].search([('code','=',template_data_code),('state','=',True),('company_id','=',company_id)], limit=1)
        if data_obj.state != True: 
            return 

        results_vars = {}
        exec(data_obj.template_content, {"record":record,"env":self.env, "_logger":_logger},results_vars)

        return results_vars["json_data"]

    
    def generic_request(self, record, url_route, method, template_type, template_code, id_process_queue, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        if not url_route or not template_code: 
                return True

        data_obj = self.env["nextconnector.template_" + template_type].search([('code','=',template_code),('state','=',True),('company_id','=',company_id)], limit=1)
        if data_obj.state != True: 
            raise Warning( " Plantilla " + template_code +  " inactiva")

        results_vars = {}
        exec(data_obj.template_content, {"record":record,"env":self.env, "_logger":_logger},results_vars)

        record_queue = self.env["nextconnector.process_queue"].sudo().browse(id_process_queue)
        if record_queue:
            record_queue.write({"json_request":results_vars["json_data"]})
        response = _rq(self,url_route,results_vars["json_data"], method, company_id)

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            return json_resp
                

    #TODO PARAMETRIZAR QUERYS DE REPRESENTANTE DE VENTAS                
    def create_sales_rep(self):

        query = """ SELECT  T1."SlpCode" AS "nxt_id_erp",  T1."SlpName" AS "nxt_name" 
                    FROM "OSLP" T1 """

        record = {
            "id": "",
            "record_type": "sales_rep",
            "fields": [
                    {"name": "query","value": query}
                ]
        }
        
        response = _rq(self,"/nextconnector/api/records/items",record,"get")

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
                            nxt_id_erp = row["nxt_id_erp"]
                            rec = self.env['nextconnector.sales_rep'].search([('nxt_id_erp','=',nxt_id_erp)])
                            if rec :
                                result = rec.write(row)
                                _logger.info("Update Vendedores !  id:" + str(result) + " - " + str(row))
                            else:
                                result = self.env['nextconnector.sales_rep'].create(row)
                                _logger.info("Create Vendedor !  id:" + str(result) + " - " + str(row))
                        except Exception as e:
                            _logger.info("Error al crear Vendedor:" + str(e))
                            raise Warning("Error al crear Vendedor :" + str(e))
        
    


    
    