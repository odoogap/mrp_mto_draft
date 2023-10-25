from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_from_so_configuration_product = fields.Boolean(string="From SO Configuration Product",
                                                    compute='_compute_from_so_congiguration_product')

    def _compute_from_so_congiguration_product(self):
        for picking in self:
            picking.is_from_so_configuration_product = False
            if all(move.is_from_so_configuration_product is True for move in picking.move_ids_without_package):
                picking.is_from_so_configuration_product = True
