# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class BudgetDetail(models.Model):
    _name = "budget.detail"
    _description = "Budget Detail"

    @api.depends(
        "amount_unit",
        "quantity",
    )
    @api.multi
    def _compute_amount_subtotal(self):
        for document in self:
            document.amount_subtotal = document.amount_unit * document.quantity

    @api.depends("product_id")
    @api.multi
    def _compute_allowed_uom_ids(self):
        obj_uom = self.env["product.uom"]
        for document in self:
            result = []
            if document.product_id:
                uom_categ = document.product_id.uom_id.category_id
                criteria = [("category_id", "=", uom_categ.id)]
                result = obj_uom.search(criteria).ids
            document.allowed_uom_ids = result

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="budget.budget",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Description",
        required=True,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
    )
    amount_unit = fields.Float(
        string="Amount Per Unit",
        required=True,
        default=0.0,
    )
    quantity_computation_id = fields.Many2one(
        string="Quantity Computation",
        comodel_name="budget.quantity_computation",
    )
    quantity = fields.Float(
        string="Qty.",
        required=True,
        default=1.0,
    )
    allowed_uom_ids = fields.Many2many(
        string="Allowed UoMs",
        comodel_name="product.uom",
        compute="_compute_allowed_uom_ids",
        store=False,
    )
    uom_id = fields.Many2one(
        string="UoM",
        comodel_name="product.uom",
    )
    amount_subtotal = fields.Float(
        string="Amount Subtotal",
        compute="_compute_amount_subtotal",
        store=True,
    )

    @api.multi
    def action_recompute_quantity(self):
        for document in self:
            document.onchange_quantity()

    @api.onchange(
        "product_id",
    )
    def onchange_name(self):
        self.name = ""
        if self.product_id:
            self.name = self.product_id.name

    @api.onchange(
        "product_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False

    @api.onchange(
        "quantity_computation_id",
    )
    def onchange_quantity(self):
        if self.quantity_computation_id:
            quantity = self.quantity_computation_id._get_qty(self)
            self.quantity = quantity

    @api.onchange(
        "product_id",
        "pricelist_id",
        "quantity",
    )
    def onchange_amount_unit(self):
        self.amount_unit = 0.0
        if self.product_id and self.pricelist_id:
            price_unit = self.pricelist_id.price_get(
                prod_id=self.product_id.id, qty=1.0
            )[self.pricelist_id.id]
            self.amount_unit = price_unit
