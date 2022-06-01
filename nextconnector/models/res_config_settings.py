# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    env_production = fields.Boolean("Activar ambiente de producción?")
    url_api = fields.Char("URL API")
    user_api = fields.Char("Usuario API")
    pwd_api = fields.Char("Password API")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['env_production'] = self.env['ir.config_parameter'].sudo().get_param('nextconnector.env_production', default=False)
        res['url_api'] = str(self.env['ir.config_parameter'].sudo().get_param('nextconnector.url_api', default=""))
        res['user_api'] = str(self.env['ir.config_parameter'].sudo().get_param('nextconnector.user_api', default=""))
        res['pwd_api'] = str(self.env['ir.config_parameter'].sudo().get_param('nextconnector.pwd_api', default=""))
        
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('nextconnector.env_production', self.env_production)
        self.env['ir.config_parameter'].sudo().set_param('nextconnector.url_api', self.url_api)
        self.env['ir.config_parameter'].sudo().set_param('nextconnector.user_api', self.user_api)
        self.env['ir.config_parameter'].sudo().set_param('nextconnector.pwd_api', self.pwd_api)

        super(ResConfigSettings, self).set_values()  