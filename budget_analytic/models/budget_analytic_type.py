# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class BudgetAnalyticType(models.Model):
    _name = "budget_analytic.type"
    _description = "Analytic Budget Type"

    @api.multi
    def _compute_allowed_revenue_account(self):
        for record in self:
            result = []
            result += record.allowed_revenue_account_ids.ids
            for product in record.revenue_account_ids:
                result.append(product.account_id.id)
            record.all_allowed_revenue_account_ids = result

    @api.multi
    def _compute_allowed_cost_account(self):
        for record in self:
            result = []
            result += record.allowed_cost_account_ids.ids
            for product in record.cost_account_ids:
                result.append(product.account_id.id)
            record.all_allowed_cost_account_ids = result

    name = fields.Char(
        string="Analytic Budget Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        relation="rel_budget_analytic_type_2_account",
        column1="type_id",
        column2="account_id",
        domain=[("type", "not in", ["view", "consolidation", "closed"])],
    )
    allowed_revenue_account_ids = fields.Many2many(
        string="Allowed Revenue Accounts Without Product",
        comodel_name="account.account",
        relation="rel_budget_analytic_type_2_revenue_account",
        column1="type_id",
        column2="account_id",
        domain=[("type", "not in", ["view", "consolidation", "closed"])],
    )
    allowed_cost_account_ids = fields.Many2many(
        string="Allowed Cost Accounts Without Product",
        comodel_name="account.account",
        relation="rel_budget_analytic_type_2_cost_account",
        column1="type_id",
        column2="account_id",
        domain=[("type", "not in", ["view", "consolidation", "closed"])],
    )
    account_ids = fields.One2many(
        string="Allowed Account",
        comodel_name="budget_analytic.type_account",
        inverse_name="type_id",
    )
    revenue_account_ids = fields.One2many(
        string="Revenue Accounts",
        comodel_name="budget_analytic.type_account",
        inverse_name="type_id",
        domain=[
            ("direction", "=", "revenue"),
        ],
    )
    cost_account_ids = fields.One2many(
        string="Cost Accounts",
        comodel_name="budget_analytic.type_account",
        inverse_name="type_id",
        domain=[
            ("direction", "=", "cost"),
        ],
    )
    all_allowed_revenue_account_ids = fields.Many2many(
        string="All Allowed Revenue Account",
        comodel_name="account.account",
        compute="_compute_allowed_revenue_account",
        store=False,
    )
    all_allowed_cost_account_ids = fields.Many2many(
        string="All Allowed Cost Account",
        comodel_name="account.account",
        compute="_compute_allowed_cost_account",
        store=False,
    )
    budget_analytic_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Analytic Budget",
        comodel_name="res.groups",
        relation="rel_type_2_confirm_budget_analytic",
        column1="type_id",
        column2="group_id",
    )
    budget_analytic_restart_approval_grp_ids = fields.Many2many(
        string="Allow To Restart Analytic Budget Approval",
        comodel_name="res.groups",
        relation="rel_type_2_restart_approve_budget_analytic",
        column1="type_id",
        column2="group_id",
    )
    budget_analytic_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Analytic Budget",
        comodel_name="res.groups",
        relation="rel_type_2_cancel_budget_analytic",
        column1="type_id",
        column2="group_id",
    )
    budget_analytic_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Analytic Budget",
        comodel_name="res.groups",
        relation="rel_type_2_restart_budget_analytic",
        column1="type_id",
        column2="group_id",
    )
