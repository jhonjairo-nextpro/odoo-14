# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import Warning
from odoo.http import request
from odoo.addons.website.models import ir_http
import json  
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    is_b2b_address_restrictions = fields.Boolean(
        string="Desactivar edicion de datos facturación y envio",
    )

    def _get_is_b2b_address_restrictions(self):
        if self:
            return self.is_b2b_address_restrictions
        return False
    
    def _prepare_sale_order_values(self, partner, pricelist):
        self.ensure_one()
        affiliate_id = request.session.get('affiliate_id')
        salesperson_id = affiliate_id if self.env['res.users'].sudo().browse(affiliate_id).exists() else request.website.salesperson_id.id
        addr_ship = partner.address_get(['delivery'])
        addr_inv = partner.address_get(['invoice'])
        if not request.website.is_public_user():
            last_sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id)], limit=1, order="date_order desc, id desc")
            shipping_default = partner.search([
                        ("id", "child_of", partner.commercial_partner_id.ids),
                        ("type", "in", ["delivery"]),
                        ("is_default_address", "=", True),
                    ], limit=1)

            if shipping_default:
                addr_ship['delivery'] = shipping_default.id
            else:
                if last_sale_order:  # first = me
                    addr_ship['delivery'] = last_sale_order.partner_shipping_id.id

            invoice_default = partner.search([
                        ("id", "child_of", partner.commercial_partner_id.ids),
                        ("type", "in", ["invoice"]),
                        ("is_default_address", "=", True),
                    ], limit=1)

            if invoice_default:
                addr_inv['invoice'] = invoice_default.id
            else:
                if last_sale_order:  # first = me
                    addr_inv['invoice'] = last_sale_order.partner_invoice_id.id

        default_user_id = partner.parent_id.user_id.id or partner.user_id.id
        values = {
            'partner_id': partner.id,
            'pricelist_id': pricelist.id,
            'payment_term_id': self.sale_get_payment_term(partner),
            'team_id': self.salesteam_id.id or partner.parent_id.team_id.id or partner.team_id.id,
            'partner_invoice_id': addr_inv['invoice'],
            'partner_shipping_id': addr_ship['delivery'],
            'user_id': salesperson_id or self.salesperson_id.id or default_user_id,
            'website_id': self._context.get('website_id'),
        }
        company = self.company_id or pricelist.company_id
        if company:
            values['company_id'] = company.id
            if self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note'):
                values['note'] = company.sale_note or ""

        return values