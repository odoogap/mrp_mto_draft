from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_from_so_configuration_product = fields.Boolean(string="From SO Configuration Product",
                                                    compute='_compute_from_so_congiguration_product')

    def _compute_from_so_congiguration_product(self):
        for mo in self:
            is_from_so_configuration_product = False
            if mo.sale_order_count and mo.product_id.product_add_mode == 'configurator':
                is_from_so_configuration_product = True
            mo.is_from_so_configuration_product = is_from_so_configuration_product

    def _update_bom_id(self):
        self.product_uom_id = self.bom_id and self.bom_id.product_uom_id.id or self.product_id.uom_id.id
        for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id):
            move.product_uom_qty = move.bom_line_id.product_qty * self.product_qty
        self.picking_type_id = self.bom_id.picking_type_id or self.picking_type_id

    def _update_mo_from_sale(self, vals):
        if 'product_qty' in vals and not vals.get('product_qty', 0):
            self.action_cancel()
        else:
            self.write(vals)
            self._onchange_product_qty()
            self._onchange_move_finished_product()
            self._update_bom_id()
            self._create_workorder()