# -*- coding: utf-8 -*-
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        """When user change the product in confirm sales order then changed the product on the Delivery orders and
            Manufacturing orders and set the new move line ids to sale order line.
        """
        res = super().write(vals)
        if self.state == 'sale' and self.mrp_production_count:
            self.picking_ids.filtered(lambda x: x.state == 'waiting').move_lines.write({'state': 'draft'})
            products = self.order_line.mapped('product_id')
            for picking in self.picking_ids:
                stock_move = picking.move_ids_without_package.filtered(lambda x: x.product_id.id not in products.ids)
                if stock_move and stock_move.state == 'draft' and stock_move.sale_line_id:
                    new_move_ids = stock_move.sale_line_id.move_ids - stock_move
                    stock_move.sale_line_id.move_ids = new_move_ids
                    created_production_id = stock_move.created_production_id
                    new_move_ids.write(
                        {'created_production_id': created_production_id.id})
                    created_production_id.move_raw_ids.unlink()
                    stock_move._action_cancel()
                    stock_move.unlink()
                    created_production_id._onchange_product_id()
                    created_production_id._onchange_bom_id()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        self.picking_ids.filtered(lambda x: x.state == 'waiting').move_lines.write({'state': 'draft'})
        return res

    def lock_so(self):
        """Lock Documents Function."""
        self.action_done()
        procurement_groups = self.env['procurement.group'].search([('sale_id', 'in', self.ids)])
        mrp_production_ids = set(
            procurement_groups.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids) | \
                             set(procurement_groups.mrp_production_ids.ids)
        mrp_production_ids = list(mrp_production_ids)
        productions = self.env['mrp.production'].browse(mrp_production_ids)
        productions.filtered(lambda x: x.state == 'draft').action_confirm()
        self.picking_ids.filtered(lambda x: x.state == 'draft').action_confirm()
        for line in self.order_line:
            line.product_updatable = False


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_protected_fields(self):
        """Remove 'name' from protected fields."""
        fields = super()._get_protected_fields()
        fields.remove("name")
        return fields

    @api.depends('product_id', 'order_id.state', 'qty_invoiced', 'qty_delivered')
    def _compute_product_updatable(self):
        super()._compute_product_updatable()
        for line in self:
            line.product_updatable = True

    def write(self, vals):
        old_product_id = self.product_id
        return super(SaleOrderLine, self.with_context(old_product_id=old_product_id)).write(vals)
