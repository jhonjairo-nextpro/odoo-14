odoo.define("website_sale_delivery.custom_checkout", function (require) {
  "use strict";

  var core = require("web.core");
  var publicWidget = require("web.public.widget");

  var _t = core._t;
  var concurrency = require("web.concurrency");
  var dp = new concurrency.DropPrevious();

  publicWidget.registry.websiteSaleDelivery = publicWidget.Widget.extend({
    selector: ".oe_website_sale",
    events: {
      'change select[name="shipping_id"]': "_onSetAddress",
      "change #agencies, #agencia, #direccion, #direccion_courier_cliente, #nombre_courier_cliente, #numero_documento_cliente, #numero_contacto_cliente, #nombre_contacto_cliente":
        "_onSetDatosRetiraCliente",
      "click #delivery_carrier .o_delivery_carrier_select": "_onCarrierClick"
    },

    /**
     * @override
     */
    start: function () {
      var self = this;
      var $carriers = $('#delivery_carrier input[name="delivery_type"]');
      var $payButton = $("#o_payment_form_pay");
      // Workaround to:
      // - update the amount/error on the label at first rendering
      // - prevent clicking on 'Pay Now' if the shipper rating fails
      if ($carriers.length > 0) {
        if ($carriers.filter(":checked").length === 0) {
          $payButton.prop("disabled", true);
          var disabledReasons = $payButton.data("disabled_reasons") || {};
          disabledReasons.carrier_selection = true;
          $payButton.data("disabled_reasons", disabledReasons);
        }
        $carriers.filter(":checked").click();
      }

      // Asynchronously retrieve every carrier price
      _.each($carriers, function (carrierInput, k) {
        self._showLoading($(carrierInput));
        self
          ._rpc({
            route: "/shop/carrier_rate_shipment",
            params: {
              carrier_id: carrierInput.value
            }
          })
          .then(self._handleCarrierUpdateResultBadge.bind(self));
      });

      $("#delivery_carrier").click();

      return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {jQuery} $carrierInput
     */
    _showLoading: function ($carrierInput) {
      $carrierInput
        .siblings(".o_wsale_delivery_badge_price")
        .html('<span class="fa fa-spinner fa-spin"/>');
    },
    /**
     * @private
     * @param {Object} result
     */
    _handleCarrierUpdateResult: function (result) {
      this._handleCarrierUpdateResultBadge(result);
      var $payButton = $("#o_payment_form_pay");
      var $amountDelivery = $("#order_delivery .monetary_field");
      var $amountUntaxed = $("#order_total_untaxed .monetary_field");
      var $amountTax = $("#order_total_taxes .monetary_field");
      var $amountTotal = $(
        "#order_total .monetary_field, #amount_total_summary.monetary_field"
      );

      if (result.status === true) {
        $amountDelivery.html(result.new_amount_delivery);
        $amountUntaxed.html(result.new_amount_untaxed);
        $amountTax.html(result.new_amount_tax);
        $amountTotal.html(result.new_amount_total);
        var disabledReasons = $payButton.data("disabled_reasons") || {};
        disabledReasons.carrier_selection = false;
        $payButton.data("disabled_reasons", disabledReasons);
        $payButton.prop(
          "disabled",
          _.contains($payButton.data("disabled_reasons"), true)
        );
      } else {
        $amountDelivery.html(result.new_amount_delivery);
        $amountUntaxed.html(result.new_amount_untaxed);
        $amountTax.html(result.new_amount_tax);
        $amountTotal.html(result.new_amount_total);
      }
    },
    /**
     * @private
     * @param {Object} result
     */
    _handleCarrierUpdateResultBadge: function (result) {
      var $carrierBadge = $(
        '#delivery_carrier input[name="delivery_type"][value=' +
          result.carrier_id +
          "] ~ .o_wsale_delivery_badge_price"
      );

      if (result.status === true) {
        // if free delivery (`free_over` field), show 'Free', not '$0'
        if (result.is_free_delivery) {
          $carrierBadge.text(_t("Free"));
        } else {
          $carrierBadge.html(result.new_amount_delivery);
        }
        $carrierBadge.removeClass("o_wsale_delivery_carrier_error");
      } else {
        $carrierBadge.addClass("o_wsale_delivery_carrier_error");
        $carrierBadge.text(result.error_message);
      }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    /**
     * @private
     * @param {Event} ev
     */
    _onSetDatosRetiraCliente: function (ev) {
      var nombre_courier_cliente = $("#nombre_courier_cliente").val();
      var numero_documento_cliente = $("#numero_documento_cliente").val();
      var direccion_courier_cliente = $("#direccion_courier_cliente").val();
      var numero_contacto_cliente = $("#numero_contacto_cliente").val();
      var nombre_contacto_cliente = $("#nombre_contacto_cliente").val();
      var agencias = $("#agencies option:selected").val();

      var code_agencies = $("#agencies option:selected").data("code");

      // var code_agencies = $("#agencies").data("code");
      var tipo_envio = $(
        "input:radio[name='tipo_envio_agencia']:checked"
      ).val();

      var $h6_nombre_courier_cliente = $("#h6_nombre_courier_cliente");
      if (code_agencies == "00") {
        $h6_nombre_courier_cliente.removeClass("d-none");
        $h6_nombre_courier_cliente.addClass("d-inline");
      } else {
        $h6_nombre_courier_cliente.removeClass("d-inline");
        $h6_nombre_courier_cliente.addClass("d-none");
      }

      var $h6_direccion_courier_cliente = $("#h6_direccion_courier_cliente");
      if (tipo_envio == "agencia") {
        $h6_direccion_courier_cliente.removeClass("d-none");
        $h6_direccion_courier_cliente.addClass("d-inline");
      } else {
        $h6_direccion_courier_cliente.removeClass("d-inline");
        $h6_direccion_courier_cliente.addClass("d-none");
      }


      console.log("agencias ****", agencias);
      console.log("tipo_envio ****", tipo_envio);
      console.log("code agencias ****", code_agencies);

      this._rpc({
        route: "/shop/update_info_retira_cliente",
        params: {
          nombre_courier_cliente: nombre_courier_cliente,
          numero_documento_cliente: numero_documento_cliente,
          direccion_courier_cliente: direccion_courier_cliente,
          numero_contacto_cliente: numero_contacto_cliente,
          nombre_contacto_cliente: nombre_contacto_cliente,
          agencia_envio: agencias,
          tipo_envio_agencia: tipo_envio
        }
      });
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onCarrierClick: function (ev) {
      var $radio = $(ev.currentTarget).find('input[type="radio"]');

      var is_site_b2b = $("#is_site_b2b").val();
      var current_carrier_id = $("#current_carrier_id").val();
      var retiro_en_tienda = $radio.data("retiro_en_tienda");

      console.log("is_site_b2b", is_site_b2b);
      console.log("current_carrier_id", current_carrier_id);
      console.log("retiro_en_tienda", retiro_en_tienda);
      console.log("$radio", $radio);
      console.log("carrier_id", $radio.val());

      if (
        $("#delivery_carrier").data("init") === 0 &&
        retiro_en_tienda === true
      ) {
        let isExecuted = confirm(
          "Algunos productos prodrian eliminarse de su carrito si no hay " +
            "disponiblidad de stock en la sucursal seleccionada. \nesta seguro que desea continuar?"
        );
        console.log("isExecuted", isExecuted); // OK = true, Cancel = false
        if (!isExecuted) {
          return;
        }
      }

      this._showLoading($radio);
      $radio.prop("checked", true);
      var $payButton = $("#o_payment_form_pay");
      $payButton.prop("disabled", true);
      var disabledReasons = $payButton.data("disabled_reasons") || {};
      disabledReasons.carrier_selection = true;
      $payButton.data("disabled_reasons", disabledReasons);
      dp.add(
        this._rpc({
          route: "/shop/update_carrier",
          params: {
            carrier_id: $radio.val()
          }
        })
      ).then(this._handleCarrierUpdateResult.bind(this));

      console.log(
        "Entro a recargar pagina before:",
        $("#delivery_carrier").data("init")
      );
      if ($("#delivery_carrier").data("init") === 0) {
        window.setTimeout(function () {
          location.reload();
        }, 1000);

        $("#delivery_carrier").data("init", 0);
      } else {
        $("#delivery_carrier").data("init", 0);
      }
      console.log(
        "Entro a recargar pagina after",
        $("#delivery_carrier").data("init")
      );
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onSetAddress: function (ev) {
      var value = $(ev.currentTarget).val();
      var $providerFree = $(
        'select[name="country_id"]:not(.o_provider_restricted), select[name="state_id"]:not(.o_provider_restricted)'
      );
      var $providerRestricted = $(
        'select[name="country_id"].o_provider_restricted, select[name="state_id"].o_provider_restricted'
      );
      if (value === 0) {
        // Ship to the same address : only show shipping countries available for billing
        $providerFree.hide().attr("disabled", true);
        $providerRestricted.show().attr("disabled", false).change();
      } else {
        // Create a new address : show all countries available for billing
        $providerFree.show().attr("disabled", false).change();
        $providerRestricted.hide().attr("disabled", true);
      }
    }
  });
});
