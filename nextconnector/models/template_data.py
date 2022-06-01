import logging
from odoo import models, fields, api
from odoo.exceptions import Warning

import requests
_logger = logging.getLogger(__name__)

class NextConnectorTemplateData(models.Model):
    _name = 'nextconnector.template_data'
    _description = 'Plantillas de configuración de datos'

    code = fields.Char('Codigo')
    description = fields.Char('Descripcion')
    template_content = fields.Text('Pantilla de configuración')
    model = fields.Many2one("ir.model")
    state = fields.Boolean('Activo')
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
    default=lambda self: self.env.company)