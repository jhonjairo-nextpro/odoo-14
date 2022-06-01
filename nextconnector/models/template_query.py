import logging
from odoo import models, fields, api
from odoo.exceptions import Warning

import requests
_logger = logging.getLogger(__name__)

class NextConnectorTemplateQuery(models.Model):
    _name = 'nextconnector.template_query'
    _description = 'Plantillas de configuración de consultas'

    code = fields.Char('Codigo')
    description = fields.Char('Descripcion')
    template_content = fields.Text('Pantilla de configuración')
    model = fields.Many2one("ir.model")
    state = fields.Boolean('Activo')
    company_id = fields.Many2one('res.company', string='Compañia', required=True,
    default=lambda self: self.env.company)