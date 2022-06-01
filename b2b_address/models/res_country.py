# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)

class ResCountry(models.Model):
    _inherit = 'res.country'
    
    def get_website_sale_countries(self, mode='billing'):
        return self.sudo().search([('code', '=', 'PE')], limit=1)

    def get_website_sale_states(self, mode='billing'):
        #res = super(ResCountry, self).get_website_sale_states(mode=mode)

        states = self.env['res.country.state']
        states = states.search([('country_id.code', '=', 'PE')], order='name asc')
        _logger.info("states :" + str(states))
        return states