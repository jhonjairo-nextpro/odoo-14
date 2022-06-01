odoo.define('website.b2b_address', function(require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.websiteSaleCart = publicWidget.Widget.extend({
        selector: '.oe_website_sale .oe_cart',
        events: {
            'click .js_change_shipping': '_onClickChangeShipping',
            'click .js_change_invoicing': '_onClickChangeInvoicing',
            'click .js_edit_address': '_onClickEditAddress',
            'click .js_delete_product': '_onClickDeleteProduct',
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @param {Event} ev
         */
        _onClickChangeShipping: function (ev) {
            ev.preventDefault();
            var $old = $('.all_shipping').find('.card.border.border-primary');
            $old.find('.btn-ship').toggle();
            $old.addClass('js_change_shipping');
            $old.removeClass('border border-primary');
    
            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-ship').toggle();
            $new.removeClass('js_change_shipping');
            $new.addClass('border border-primary');
    
            var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
            $.post($form.attr('action'), $form.serialize()+'&xhr=1');
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onClickChangeInvoicing: function (ev) {
            ev.preventDefault();
            var $old = $('.all_invoicing').find('.card.border.border-primary');
            $old.find('.btn-ship').toggle();
            $old.addClass('js_change_invoicing');
            $old.removeClass('border border-primary');
    
            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-ship').toggle();
            $new.removeClass('js_change_invoicing');
            $new.addClass('border border-primary');
    
            var $form = $(ev.currentTarget).parent('div.one_kanban').find('form.d-none');
            $.post($form.attr('action'), $form.serialize()+'&xhr=1');
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onClickEditAddress: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).closest('div.one_kanban').find('form.d-none').attr('action', '/shop/address').submit();
        },
        /**
         * @private
         * @param {Event} ev
         */
        _onClickDeleteProduct: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).closest('tr').find('.js_quantity').val(0).trigger('change');
        },
    });
    

});