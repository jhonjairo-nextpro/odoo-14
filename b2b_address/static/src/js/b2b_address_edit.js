odoo.define('custommodule.website_sale_b2b', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    require('website_sale.website_sale');
    
    publicWidget.registry.CustomWebSiteSaleB2B = publicWidget.Widget.extend({
            selector: '.oe_website_sale',
            events: {
                'change input[name="primer_nombre"]': '_onChangeNames',
                'change input[name="segundo_nombre"]': '_onChangeNames',
                'change input[name="name"]': '_onChangeRazonSocial',
                'change input[name="vat"]': '_onChangeVat',
                'change input[name="street"]': '_onChangeStreet',
                'click .a-submit-fiscal-info': '_onClickSubmitFiscallInfo',
                'submit .a-submit-fiscal-info': '_onClickSubmitFiscallInfo',
                'change select[name="state_id"]': '_onChangeState',
                'change select[name="tipo_documento"]': '_onChangeTipoDocumento',
                'change select[name="city_id"]': '_onChangeCity',
            },
            /**
             * @override
             */
            start: function () {
                var def = this._super.apply(this, arguments);
                this.$('select[name="state_id"]').change();
                this.$('select[name="city_id"]').change();
    
                var $tipo_persona = $("#tipo_persona");
                var $tipo_documento = $("#tipo_documento");
                var $div_name = $(".div_name");
                var $label_vat = $(".label_vat");
                var $lbl_direccion = $(".lbl_direccion");
                var $tipo_documento = $("#tipo_documento");
                
                var $checkbox = $(".checkbox");
                if ($tipo_documento.val() == "boleta"){
                    //$tipo_documento.attr('disabled', false);
                    $div_name.addClass('d-none');
                    $label_vat.text("DNI*");
                    $lbl_direccion.text("Dirección de Envío");
                    $checkbox.addClass('d-none');
                }else{
                    //$tipo_documento.attr('disabled', true);
                    $div_name.removeClass('d-none');
                    $label_vat.text("RUC*");
                    $lbl_direccion.text("Dirección de Facturación");
                    $checkbox.removeClass('d-none');
                }
                var $country_id = $("#country_id");
                if($country_id.val()==""){
                    $("#country_id option[value='173']").prop("selected", true);
                }

                var $state_id = $("#state_id");
                if($state_id.val()==""){
                    $("#state_id option[value='']").prop("selected", true);
                }

                return def;
            },
            //--------------------------------------------------------------------------
            // Private
            //--------------------------------------------------------------------------
            /**
             * @private
             * @param {Event} ev
             */
            _onChangeNames: function (ev) {
    
                var $input = $(ev.currentTarget);
                var $primer_nombre = $('input[name="primer_nombre"]');
                var $segundo_nombre = $('input[name="segundo_nombre"]');
    
                var primer_nombre = $primer_nombre.val();
                if(primer_nombre.toUpperCase() !== $primer_nombre.val()){
                    $primer_nombre.val(primer_nombre.toUpperCase())
                }
    
                var segundo_nombre = $segundo_nombre.val();
                if(segundo_nombre.toUpperCase() !== $segundo_nombre.val()){
                    $segundo_nombre.val(segundo_nombre.toUpperCase())
                }
    
                var $name = $('input[name="name"]');
                //var fullname = $segundo_nombre.val() + (String($primer_nombre.val()).length>0?" ":"") + $primer_nombre.val(); 
                var fullname = $primer_nombre.val() + (String($segundo_nombre.val()).length>0?" ":"") + $segundo_nombre.val(); 
                console.info(fullname);
                $name.val(fullname);
    
            },
            _onChangeRazonSocial: function (ev) {
    
                var $input = $(ev.currentTarget);
                var $name = $('input[name="name"]');
    
                var name = $name.val();
                if(name.toUpperCase() !== $name.val()){
                    $name.val(name.toUpperCase())
                }
            },
            _onChangeVat: function (ev) {
    
                var $input = $(ev.currentTarget);
                var $vat = $('input[name="vat"]');
    
                var vat = $vat.val();
                if(vat.toUpperCase() !== $vat.val()){
                    $vat.val(vat.toUpperCase())
                }
            },
            _onChangeStreet: function (ev) {
    
                var $input = $(ev.currentTarget);
                var $name = $('input[name="street"]');
    
                var name = $name.val();
                if(name.toUpperCase() !== $name.val()){
                    $name.val(name.toUpperCase())
                }
            },
            _onChangeTipoDocumento: function (ev) {
                
                var $tipo_persona = $("#tipo_persona");
                var $tipo_documento = $("#tipo_documento");
                var $div_tipo_identificacion = $(".div_tipo_identificacion");
                var $tipo_identificacion = $("#tipo_identificacion");
                var $div_name = $(".div_name");
                var $label_vat = $(".label_vat");
    
                if (!$tipo_persona.val()) {
                    return;
                }
                var $lbl_direccion = $(".lbl_direccion");
                var $checkbox = $(".checkbox");
                var $tipo_documento = $("#tipo_documento");
                if ($tipo_documento.val() == "boleta"){
                    //$tipo_documento.attr('disabled', false);
                    $div_name.addClass('d-none');
                    $label_vat.text("DNI*");
                    $lbl_direccion.text("Dirección de Envío");
                    $checkbox.addClass('d-none');
                    $div_tipo_identificacion.removeClass('d-none');
                    if($tipo_identificacion.val()!="1"){
                        $("#tipo_identificacion option[value='1']").prop("selected", true);
                    }
                }else{
                    //$tipo_documento.attr('disabled', true);
                    $div_name.removeClass('d-none');
                    $label_vat.text("RUC*");
                    $lbl_direccion.text("Dirección de Facturación");
                    $checkbox.removeClass('d-none');
                    $div_tipo_identificacion.addClass('d-none');
                    if($tipo_identificacion.val()!="6"){
                        $("#tipo_identificacion option[value='1']").prop("selected", true);
                    }
                }
    
            },
            disableButton: function (button) {
                if (!$(button).attr('disabled')){
                    $(button).attr('disabled', true);
                    $(button).children('.fa-lock').removeClass('fa-lock');
                    $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
                }
            },
        
            enableButton: function (button) {
                if ($(button).attr('disabled')){
                    $(button).attr('disabled', false);
                    $(button).children('.fa').addClass('fa-lock');
                    $(button).find('span.o_loader').remove();
                }
            },
            /**
             * @private
             * @param {Event} ev
             * @returns {Promise}
             */
            _submitCode: function (ev) {
                if (ev.type === 'submit') {
                    var button = $('#btn-primary');
                } else {
                    var button = ev.target;
                }
                
                var $aSubmit = $(ev.currentTarget);
                this.disableButton(button);
                var modeaddress = $('#modeaddress').val();
                if(modeaddress !== "billing"){
                    $aSubmit.closest('form').submit();
                    return;
                }
    
                console.info("button",button);
                var $input = $(ev.currentTarget);
                var flagError = false;
    
                if(!flagError){
                    $aSubmit.closest('form').submit();
                }
                
            },
            /**
             * @private
             */
            _changeState: function () {
                console.log('$("#state_id").val()', $("#state_id").val());
                if (!$("#state_id").val()) {
                    return;
                }
                this._rpc({
                    route: "/shop/cities_infos/" + $("#state_id option:selected").val(),
                    params: {
                        mode:'shipping'
                    },
                }).then(function (array_data) {
                    // placeholder phone_code
                    //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');
    
                    // populate states and display
                    var selectCities = $("select[name='city_id']");
                    // dont reload state at first loading (done in qweb)
                    if (selectCities.data('init')===0 || selectCities.find('option').length===1) {
                        if (array_data.length) {
                            console.log('array_data', array_data);
                            selectCities.html('');
                            var opt = $('<option>').text('Provincia...')
                                    .attr('value', '');
                                selectCities.append(opt);
    
                            _.each(array_data, function (x) {
                                var opt = $('<option>').text(x.name)
                                    .attr('value', x.id);
                                selectCities.append(opt);
                            });
                            selectCities.parent('div').show();
                        } else {
                            selectCities.val('').parent('div').hide();
                            
                        }
                        selectCities.data('init', 0);
                    } else {
                        selectCities.data('init', 0);
                    }
    
                    // manage fields order / visibility
                    if (array_data.fields) {
                        _.each(all_fields, function (field) {
                            $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                        });
                    }
                });
            },
            /**
             * @private
             * @param {Event} ev
             */
            _onChangeState: function (ev) {
                if (!this.$('.checkout_autoformat').length) {
                    return;
                }
                this._changeState();
            },
    
            /**
             * @private
             */
            _changeCity: function () {
                console.log('$("#city_id").val()', $("#city_id").val());
                if (!$("#city_id").val()) {
                    return;
                }
                this._rpc({
                    route: "/shop/districts_infos/" + $("#city_id option:selected").val(),
                    params: {
                    },
                }).then(function (array_data) {
                    // placeholder phone_code
                    //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');
    
                    // populate states and display
                    var selectDistricts = $("select[name='l10n_pe_district']");
                    // dont reload state at first loading (done in qweb)
                    if (selectDistricts.data('init')===0 || selectDistricts.find('option').length===1) {
                        if (array_data.length) {
                            console.log('array_data', array_data);
                            selectDistricts.html('');
                            var opt = $('<option>').text('Distrito...')
                                    .attr('value', '');
                                    selectDistricts.append(opt);
    
                            _.each(array_data, function (x) {
                                var opt = $('<option>').text(x.name)
                                    .attr('value', x.id);
                                    selectDistricts.append(opt);
                            });
                            selectDistricts.parent('div').show();
                        } else {
                            selectDistricts.val('').parent('div').hide();
                            
                        }
                        selectDistricts.data('init', 0);
                    } else {
                        selectDistricts.data('init', 0);
                    }
    
                    // manage fields order / visibility
                    if (array_data.fields) {
                        _.each(all_fields, function (field) {
                            $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                        });
                    }
                });
            },
            /**
             * @private
             * @param {Event} ev
             */
            _onChangeCity: function (ev) {
                if (!this.$('.checkout_autoformat').length) {
                    return;
                }
                this._changeCity();
            },
            
            

            //--------------------------------------------------------------------------
            // Handlers
            //--------------------------------------------------------------------------
            /**
             * @private
             * @param {Event} ev
             */
            _onClickSubmitFiscallInfo: function (ev) {
                if (!ev.isDefaultPrevented()) {
                    ev.preventDefault();
                    
                    this._submitCode(ev);
                }
            }
    });
    
    publicWidget.registry.WebsiteSale.include({
        /**
         * Adds the stock checking to the regular _onChangeCombination method
         * @override
         */
         _changeCountry: function () {
            if (!$("#country_id").val()) {
                return;
            }
            this._rpc({
                route: "/shop/country_infos/" + $("#country_id").val(),
                params: {
                    mode: $("#country_id").attr('mode'),
                },
            }).then(function (data) {
                // placeholder phone_code
                $("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');
    
                // populate states and display
                var selectStates = $("select[name='state_id']");
                // dont reload state at first loading (done in qweb)
                if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                    if (data.states.length || data.state_required) {
                        selectStates.html('');
                        var opt = $('<option>').text('Departamento...')
                        .attr('value', '');
                        selectStates.append(opt);
    
                        _.each(data.states, function (x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0])
                                .attr('data-code', x[2]);
                            selectStates.append(opt);
                        });
                        var $state_id = $("#state_id");
                        if($state_id.val()==""){
                            $("#state_id option[value='']").prop("selected", true);
                        }
                        selectStates.parent('div').show();
                    } else {
                        selectStates.val('').parent('div').hide();
                    }
                    selectStates.data('init', 0);
                } else {
                    selectStates.data('init', 0);
                }
    
                // manage fields order / visibility
                if (data.fields) {
                    if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                        $(".div_zip").before($(".div_city"));
                    } else {
                        $(".div_zip").after($(".div_city"));
                    }
                    var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                    _.each(all_fields, function (field) {
                        $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                    });
                }
    
                if ($("label[for='zip']").length) {
                    $("label[for='zip']").toggleClass('label-optional', !data.zip_required);
                    $("label[for='zip']").get(0).toggleAttribute('required', !!data.zip_required);
                }
                if ($("label[for='zip']").length) {
                    $("label[for='state_id']").toggleClass('label-optional', !data.state_required);
                    $("label[for='state_id']").get(0).toggleAttribute('required', !!data.state_required);
                }
            });
         }
    });


    
    });