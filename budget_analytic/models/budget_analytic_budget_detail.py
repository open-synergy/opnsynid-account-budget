# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class BudgetAnalyticBudgetDetail(models.Model):
    _name = "budget_analytic.budget_detail"
    _description = "Analytic Budget Detail"

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

    @api.depends(
        "type_id",
        "direction",
    )
    @api.multi
    def _compute_allowed_account(self):
        for record in self:
            result = []
            if record.direction == "revenue":
                result = record.type_id.all_allowed_revenue_account_ids.ids
            elif record.direction == "cost":
                result = record.type_id.all_allowed_cost_account_ids.ids
            record.allowed_account_ids = result

    @api.depends(
        "type_id",
        "direction",
        "account_id",
    )
    @api.multi
    def _compute_allowed_product(self):
        obj_allowed = self.env["budget_analytic.type_account"]
        for record in self:
            result_product = []
            result_categ = []
            product_required = False
            if record.account_id:
                criteria = [
                    ("type_id", "=", record.type_id.id),
                    ("account_id", "=", record.account_id.id),
                ]
                alloweds = obj_allowed.search(criteria)
                if len(alloweds) > 0:
                    allowed = alloweds[0]
                    product_required = True
                    result_product = allowed.allowed_product_ids.ids
                    result_categ = allowed.allowed_product_categ_ids.ids
            record.allowed_product_ids = result_product
            record.allowed_product_categ_ids = result_categ
            record.product_required = product_required

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="budget_analytic.budget",
        required=True,
        ondelete="cascade",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="budget_analytic.type",
        related="budget_id.type_id",
        store=False,
    )
    name = fields.Char(
        string="Description",
        required=True,
    )
    product_required = fields.Boolean(
        string="Product Required",
        compute="_compute_allowed_product",
        store=False,
    )
    allowed_product_categ_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        compute="_compute_allowed_product",
        store=False,
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        compute="_compute_allowed_product",
        store=False,
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        compute="_compute_allowed_account",
        store=False,
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
    )
    direction = fields.Selection(
        string="Direction",
        selection=[
            ("revenue", "Revenue"),
            ("cost", "Cost"),
        ],
        required=True,
        default="revenue",
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

    @api.onchange(
        "product_id",
    )
    def onchange_name(self):
        self.name = ""
        if self.product_id:
            self.name = self.product_id.name

    @api.onchange(
        "account_id",
    )
    def onchange_product_id(self):
        self.product_id = False

    @api.onchange(
        "product_id",
    )
    def onchange_uom_id(self):
        self.uom_id = False
        if self.product_id:
            self.uom_id = self.product_id.uom_id

    @api.onchange(
        "product_id",
        "pricelist_id",
    )
    def onchange_amount_unit(self):
        self.amount_unit = 0.0
        if self.product_id and self.pricelist_id:
            # TODO: Qty aware computation
            price_unit = self.pricelist_id.price_get(
                prod_id=self.product_id.id, qty=1.0
            )[self.pricelist_id.id]
            self.amount_unit = price_unit
