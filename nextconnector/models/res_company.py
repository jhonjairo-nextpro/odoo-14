# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    env_production = fields.Boolean("Activar ambiente de producción?")
    url_api = fields.Char("URL API")
    user_api = fields.Char("Usuario API")
    pwd_api = fields.Char("Password API")
