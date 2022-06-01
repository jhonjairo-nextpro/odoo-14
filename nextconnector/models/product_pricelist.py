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

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'
    nxt_id_erp = fields.Char('Código ERP')


    def post_product_pricelist(self, params, company_id = None):

        if not company_id:
            company_id = self.env.company.id

        data_obj = self.env["nextconnector.template_query"].search([('code','=',"data_product_pricelist"),('state','=',True),('company_id','=',company_id) ], limit=1)
        if not data_obj: 
            return True

        results_vars = {}
        exec(data_obj.template_content, {"env":self.env, "record": params , "_logger":_logger},results_vars)

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
                        data_obj = self.env["nextconnector.template_query"].search([('code','=',"normalize_data_product_pricelist"),('state','=',True),('company_id','=',company_id) ], limit=1)
                        if data_obj.state != True: 
                                return True

                        results_vars = {}
                        exec(data_obj.template_content, {"env":self.env, "record": list_data["data"] , "_logger":_logger},results_vars)

                        _logger.error("INFO POST :" + str(results_vars["json_data"]))
                    except Exception as e:
                        _logger.info("Error al crear lista de precio :" + str(e))
                        raise Warning("Error al crear lista de precio :" + str(e))