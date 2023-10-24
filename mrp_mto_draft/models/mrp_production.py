from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_from_so_configuration_product = fields.Boolean(string="From SO Configuration Product",
                                                      compute='_compute_from_so_congiguration_product')

    def _compute_from_so_congiguration_product(self):
        for mo in self:
            mo.is_from_so_configuration_product = False
            if mo.sale_order_count and mo.product_id.product_add_mode == 'configurator':
                mo.is_from_so_configuration_product = True
