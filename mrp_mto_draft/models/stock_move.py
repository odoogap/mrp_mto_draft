from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_from_so_configuration_product = fields.Boolean(string="From SO Configuration Product",
                                                      compute='_compute_from_so_congiguration_product')

    def _compute_from_so_congiguration_product(self):
        for mv in self:
            mv.is_from_so_configuration_product = False
            if mv.sale_line_id and mv.product_id.product_add_mode == 'configurator':
                mv.is_from_so_configuration_product = True



