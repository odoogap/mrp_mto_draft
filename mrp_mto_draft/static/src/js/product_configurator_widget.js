odoo.define('mrp_mto_draft.product_configurator', function (require) {

var ProductConfiguratorWidget = require('sale.product_configurator');

ProductConfiguratorWidget.include({
    /**
     * Override of sale.product_configurator Hook to make Edit pencil icon visible on confirm sale order line.
     *
     * @override
    */
   _render: function () {
        this._super.apply(this, arguments);
        if (this.mode === 'edit' && this.value &&
        (this._isConfigurableProduct() || this._isConfigurableLine())) {
            this._addProductLinkButton();
            this._addConfigurationEditButton();
        } else if ((this.mode === 'edit' || this.mode === 'readonly') && this.value) {
            this._addProductLinkButton();
            this.$('.o_edit_product_configuration').hide();
        } else {
            this.$('.o_external_button').hide();
            this.$('.o_edit_product_configuration').hide();
        }
    },
});

return ProductConfiguratorWidget;

});
