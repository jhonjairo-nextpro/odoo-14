# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, tools, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CustomWebsiteSale(WebsiteSale):

    
    @http.route(['/shop/set_delivery_day'], type='json', auth="public", methods=['POST'], website=True)
    def set_delivery_day(self, **post):
        if post.get('delivery_date'):
            order = request.website.sale_get_order().sudo()

            if order and order.id:
                values = {}

                p_date = None
                if post.get('delivery_date'):
                    p_date = datetime.strptime(post.get('delivery_date') + " 14:00:00", '%d/%m/%Y %H:%M:%S')
                    
                if order:
                    if p_date:
                        _logger.info("set_delivery_day p_date :" + str(p_date))
                        values.update({
                            'commitment_date': p_date                        
                        })

                order.write(values)
        return True

    @http.route(['/shop/update_info_retira_cliente'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_info_retira_cliente(self, **post):
        order = request.website.sale_get_order()
        nombre_courier_cliente = ""
        if 'nombre_courier_cliente' in post:
            nombre_courier_cliente = str(post['nombre_courier_cliente'])
        numero_contacto_cliente = ""
        if 'numero_contacto_cliente' in post:
            numero_contacto_cliente = str(post['numero_contacto_cliente'])

        numero_documento_cliente = str(post['numero_documento_cliente'])
        nombre_contacto_cliente = str(post['nombre_contacto_cliente'])
        
        agencia_envio = False
        if 'agencia_envio' in post:
            agencia_envio = str(post['agencia_envio'])

        tipo_envio_agencia = False
        if 'tipo_envio_agencia' in post:
            tipo_envio_agencia = str(post['tipo_envio_agencia'])
        
        direccion_courier_cliente = False
        if 'direccion_courier_cliente' in post:
            direccion_courier_cliente = str(post['direccion_courier_cliente'])
        
        if order:
            order.write({
                "nombre_courier_cliente":nombre_courier_cliente
                , "numero_documento_cliente":numero_documento_cliente
                , "numero_contacto_cliente":numero_contacto_cliente
                , "nombre_contacto_cliente":nombre_contacto_cliente
                , "agencia_envio":agencia_envio
                , "tipo_envio_agencia":tipo_envio_agencia
                , "direccion_courier_cliente":direccion_courier_cliente
            })

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', 'PE')], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        city_id = 0
        l10n_pe_district = 0
        street_number = ""
        street_number2 = ""
        tipo_persona = ""
        tipo_documento = ""
        tipo_identificacion = ""
        partnerId = int(kw.get('partner_id', -1))
        _logger.info("kw :" + str(kw))
        if partnerId > 0:
            partnerObj = request.env['res.partner'].sudo().browse(partnerId)
            if 'submitted' in kw:
                self.updateInformation(partnerObj, kw)
            if partnerObj.city_id:
                city_id = partnerObj.city_id.id
            if partnerObj.l10n_pe_district:
                l10n_pe_district = partnerObj.l10n_pe_district.id
            if partnerObj.street_number:
                street_number = partnerObj.street_number
            if partnerObj.street_number2:
                street_number2 = partnerObj.street_number2
            if partnerObj.tipo_persona:
                tipo_persona = partnerObj.tipo_persona
            if partnerObj.tipo_documento:
                tipo_documento = partnerObj.tipo_documento
            if partnerObj.tipo_identificacion:
                tipo_identificacion = partnerObj.tipo_identificacion


        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            _logger.info("submitted errors :" + str(errors))

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                _logger.info("errors :" + str(errors))
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')
                    #return request.redirect('/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id

        cities = 'state_id' in values and values['state_id'] != '' and request.env['res.city'].search([('state_id','=',int(values['state_id']))])
        _logger.info("cities :" + str(cities))

        districts = 'city_id' in values and values['city_id'] != '' and request.env['l10n_pe.res.city.district'].search([('city_id','=',int(values['city_id']))])
        _logger.info("districts :" + str(districts))
        

        _logger.info("city_id :" + str(city_id))
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'city_id': city_id,
            'l10n_pe_district': l10n_pe_district,
            'street_number': street_number,
            'street_number2': street_number2,
            "tipo_persona": tipo_persona,
            "tipo_documento": tipo_documento,
            "tipo_identificacion": tipo_identificacion,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            "cities": cities,
            "districts": districts,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)

    def _get_mandatory_billing_fields(self):
        # deprecated for _get_mandatory_fields_billing which handle zip/state required
        #return ["name", "email", "street", "city", "country_id"]
        return ["name", "email", "street", "country_id"]

    def _get_mandatory_shipping_fields(self):
        # deprecated for _get_mandatory_fields_shipping which handle zip/state required
        return ["name", "street", "country_id"]

    def _get_mandatory_fields_billing(self, country_id=False):
        req = self._get_mandatory_billing_fields()
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = self._get_mandatory_shipping_fields()
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
        return req

    def _checkout_form_save(self, mode, checkout, all_values):
        res = super(CustomWebsiteSale, self)._checkout_form_save(mode, checkout, all_values)
        partnerId = int(all_values.get('partner_id', -1))
        if partnerId == -1:
            partnerObj = request.env['res.partner'].sudo().browse(res)
            if 'submitted' in all_values:
                self.updateInformation(partnerObj, all_values)
        return res

    def updateInformation(self, partnerObj, data):
        _logger.info("data :" + str(data))
        partnerObj.write({
            'primer_nombre': data.get('primer_nombre', "") or partnerObj.primer_nombre,
            'segundo_nombre': data.get('segundo_nombre', "") or partnerObj.segundo_nombre,
            'tipo_persona': data.get('tipo_persona', "") or partnerObj.tipo_persona,
            'tipo_documento': data.get('tipo_documento', "") or partnerObj.tipo_documento,
            'tipo_identificacion': data.get('tipo_identificacion', "") or partnerObj.tipo_identificacion,
            'city_id': data.get('city_id', False) or partnerObj.city_id.id,
            'l10n_pe_district': data.get('l10n_pe_district', False) or partnerObj.l10n_pe_district.id
        })
        _logger.info("city_id :" + str(partnerObj.city_id))

        return True

    #SE SOBREESCRIBE FUNCION VALIDA EL REGISTRO DEL CLIENTE
    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        # Required fields from form
        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]
        # Required fields from mandatory field function
        #SE COMENTA CAMPOS NATIVOS OBLIGATORIOS
        #required_fields += mode[1] == 'shipping' and self._get_mandatory_shipping_fields() or self._get_mandatory_billing_fields()
        # Check if state required
        _logger.info("mode :" + str(mode))
        country = request.env['res.country']
        if data.get('country_id'):
            country = country.browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'
        

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('¡Email inválido! Por favor, introduce una dirección de correo electrónico válida .'))

        if data.get('primer_nombre') and not data.get('primer_nombre').replace(" ","").strip().isalpha():
            error["primer_nombre"] = 'error'
            error_message.append(_('Solo debe ingresar letras en el campo Nombres'))
        if data.get('segundo_nombre') and not data.get('segundo_nombre').replace(" ","").strip().isalpha():
            error["segundo_nombre"] = 'error'
            error_message.append(_('Solo debe ingresar letras en el campo Apellidos'))

        

        if mode[1] == 'billing':
            if not data.get('primer_nombre'):
                error["primer_nombre"] = 'missing'
            if not data.get('segundo_nombre'):
                error["segundo_nombre"] = 'missing'

            if not data.get('vat'):
                error["vat"] = 'missing'

            if data.get('vat'):
                rut = data.get('vat')

                if len(rut) != 11 and len(rut) != 8:
                    error["vat"] = 'error'
                    error_message.append(_('El tamaño de RUC/DNI es incorrecto'))
                
                for character in rut:
                    if not character.isalnum():
                        error["vat"] = 'error'
                        error_message.append(_(f'Carácter especial no permitido ({character})'))
                        break

                tipo_documento = data.get('tipo_documento')
                if tipo_documento == "boleta" and len(rut) != 8:
                    error["vat"] = 'error'
                    error_message.append(_('El tamaño de DNI es incorrecto'))

                if tipo_documento == "factura" and len(rut) != 11:
                    error["vat"] = 'error'
                    error_message.append(_('El tamaño de RUC es incorrecto'))



        #if not data.get('sector_id') or data.get('sector_id') == "":
        #    error["sector_id"] = 'missing'
        
        if not data.get('state_id') or data.get('state_id') =="":
            error["state_id"] = 'missing'
        
        if not data.get('city_id') or data.get('city_id') =="":
            error["city_id"] = 'missing'

        if not data.get('l10n_pe_district') or data.get('l10n_pe_district') =="":
            error["l10n_pe_district"] = 'missing'
        
        if not data.get('phone') or data.get('phone') =="":
            error["phone"] = 'missing'

        if data.get('phone'):
            if len(data.get('phone')) > 10 :
                    error["phone"] = 'error'
                    error_message.append(_('El número de Teléfono es incorrecto, no debe tener más de 10 dígitos'))

        if not data.get('street'):
            error["street"] = 'missing'

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))


        return error, error_message

    #SE SOBREESCRIBE FUNCION VERIFICACION DE DIRECCION
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if request.website._get_is_b2b_address_restrictions() == False:
            if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
                return request.redirect('/shop/address')

            for f in self._get_mandatory_billing_fields():
                #SE OMITE VALIDACION DEL CAMPO CIUDAD
                if f == 'city':
                    continue
                if not order.partner_id[f]:
                    _logger.info("order.partner_id[f] :" + " Field" + str(f) + str(order.partner_id[f]))
                    return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

        values = self.checkout_values(**post)

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

 
    #SE SOBREESCRIBE FUNCION QUE RETORNA DIRECCIONES DE FACTURACION Y ENTREGA
    def checkout_values(self, **kw):
        order = request.website.sale_get_order(force_create=1)
        shippings = []
        invoices = []
        _logger.error("checkout_values kw :" + str(kw))
        if order.partner_id != request.website.user_id.sudo().partner_id:
            Partner = order.partner_id.with_context(show_address=1).sudo()
            if request.website._get_is_b2b_address_restrictions() == False:
                shippings = Partner.search([
                ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                '|', ("type", "in", ["delivery", "other"]), ("id", "=", order.partner_id.commercial_partner_id.id)
                ], order='id desc')
            else:
                shippings = Partner.search([
                    ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                    ("type", "in", ["delivery"])
                ], order='id desc')

            if shippings:
                if kw.get('partner_id') or 'use_billing' in kw:
                    if 'use_billing' in kw:
                        partner_id = order.partner_id.id
                    else:
                        partner_id = int(kw.get('partner_id'))

                    _logger.error("checkout_values shippings partner_id :" + str(partner_id))
                    if partner_id in shippings.mapped('id'):
                        order.partner_shipping_id = partner_id
                elif not order.partner_shipping_id:
                    shipping_default = Partner.search([
                        ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                        ("type", "in", ["delivery"]),
                        ("is_default_address", "=", True),
                    ], limit=1)
                    if shipping_default:
                        order.partner_shipping_id.id = shipping_default.id
                    else:
                        last_order = request.env['sale.order'].sudo().search([("partner_id", "=", order.partner_id.id)], order='id desc', limit=1)
                        order.partner_shipping_id.id = last_order and last_order.partner_shipping_id.id
            if request.website._get_is_b2b_address_restrictions() == False:
                invoices = Partner.search([
                ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                '|', ("type", "in", ["invoice", "other"]), ("id", "=", order.partner_id.commercial_partner_id.id)
                ], order='id desc')
            else:
                invoices = Partner.search([
                    ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                    ("type", "in", ["invoice", "other"])
                ], order='id desc')
            if invoices:
                if kw.get('partner_id') or 'use_billing' in kw:
                    if 'use_billing' in kw:
                        partner_id = order.partner_id.id
                    else:
                        partner_id = int(kw.get('partner_id'))
                    _logger.error("checkout_values invoices partner_id :" + str(partner_id))
                    if partner_id in invoices.mapped('id'):
                        order.partner_invoice_id = partner_id
                elif not order.partner_invoice_id:
                    invoice_default = Partner.search([
                        ("id", "child_of", order.partner_id.commercial_partner_id.ids),
                        ("type", "in", ["invoice"]),
                        ("is_default_address", "=", True),
                    ], limit=1)
                    if invoice_default:
                        order.partner_invoice_id.id = invoice_default.id
                    else:
                        last_order = request.env['sale.order'].sudo().search([("partner_id", "=", order.partner_id.id)], order='id desc', limit=1)
                        order.partner_invoice_id.id = last_order and last_order.partner_invoice_id.id

        values = {
            'order': order,
            'shippings': shippings,
            'invoices': invoices,
            'only_services': order and order.only_services or False
        }
        return values



    @http.route(['/shop/cities_infos/<model("res.country.state"):state>'], type='json', auth="public", methods=['POST'], website=True)
    def cities_infos(self, state, mode, **kw):
        _logger.info("state.id :" + str(state.id))
        cities = request.env['res.city'].sudo().search([("state_id", "=", state.id)], order='name asc')
        cities_array = []
        for citi in cities:
            cities_array.append({"id":citi.id, "name":citi.name})
        _logger.info("cities_array :" + str(cities_array))
        return cities_array

    @http.route(['/shop/districts_infos/<model("res.city"):city_id>'], type='json', auth="public", methods=['POST'], website=True)
    def districts_infos(self, city_id, **kw):
        _logger.info("city_id.id :" + str(city_id.id))
        districts = request.env['l10n_pe.res.city.district'].sudo().search([("city_id", "=", city_id.id)], order='name asc')
        districts_array = []
        for district in districts:
            districts_array.append({"id":district.id, "name":district.name})
        _logger.info("districts_array :" + str(districts_array))
        return districts_array
        
    #PARCHE
    @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def country_infos(self, country, mode='shipping', **kw):
        return dict(
            fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in country.get_website_sale_states(mode=mode)],
            phone_code=country.phone_code
        )

    
    @http.route(['/shop/carrier_rate_shipment'], type='json', auth='public', methods=['POST'], website=True)
    def cart_carrier_rate_shipment(self, carrier_id, **kw):
        order = request.website.sale_get_order(force_create=True)

        if not int(carrier_id) in order._get_delivery_methods().ids:
            raise UserError(_('It seems that a delivery method is not compatible with your address. Please refresh the page and try again.'))

        Monetary = request.env['ir.qweb.field.monetary']

        res = {'carrier_id': carrier_id}
        carrier = request.env['delivery.carrier'].sudo().browse(int(carrier_id))
        rate = carrier.rate_shipment(order)
        if rate.get('success'):
            tax_ids = carrier.product_id.taxes_id.filtered(lambda t: t.company_id == order.company_id)
            if tax_ids:
                fpos = order.fiscal_position_id
                tax_ids = fpos.map_tax(tax_ids, carrier.product_id, order.partner_shipping_id)
                taxes = tax_ids.compute_all(
                    rate['price'],
                    currency=order.currency_id,
                    quantity=1.0,
                    product=carrier.product_id,
                    partner=order.partner_shipping_id,
                )
                if request.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                    rate['price'] = taxes['total_excluded']
                else:
                    rate['price'] = taxes['total_included']

            res['status'] = True
            res['new_amount_delivery'] = Monetary.value_to_html(rate['price'], {'display_currency': order.currency_id})
            res['is_free_delivery'] = not bool(rate['price'])
            res['error_message'] = rate['warning_message']
        else:
            res['status'] = False
            res['new_amount_delivery'] = Monetary.value_to_html(0.0, {'display_currency': order.currency_id})
            res['error_message'] = rate['error_message']
        
        _logger.info("cart_carrier_rate_shipment :" + str(res))
        return res