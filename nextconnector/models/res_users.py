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
    _inherit = 'res.users'
    
    nxt_id_erp = fields.Char('Código ERP')

   