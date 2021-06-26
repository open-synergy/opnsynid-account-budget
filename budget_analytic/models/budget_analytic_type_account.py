# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class BudgetAnalyticTypeAccount(models.Model):
    _name = "budget_analytic.type_account"
    _description = "Analytic Budget Type Account"

    type_id = fields.Many2one(
        string="Analytic Budget Type",
        comodel_name="budget_analytic.type",
    )
    direction = fields.Selection(
        string="Direction",
        selection=[
            ("revenue", "Revenue"),
            ("cost", "Cost"),
        ],
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
    )
    allowed_product_categ_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        relation="rel_budget_analytic_type_account_2_product_categ",
        column1="type_id",
        column2="category_id",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        relation="rel_budget_analytic_type_account_2_product",
        column1="type_id",
        column2="product_id",
    )
