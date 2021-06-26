# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class BudgetAnalyticBudget(models.Model):
    _name = "budget_analytic.budget"
    _description = "Analytic Budget"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "base.cancel.reason_common",
        "tier.validation",
    ]
    _state_from = ["draft", "confirm"]
    _state_to = ["valid"]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_user_id(self):
        return self.env.user.id

    name = fields.Char(
        string="# Analytic Budget",
        default="/",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        copy=False,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    user_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.users",
        default=lambda self: self._default_user_id(),
        help="Person who responsible to this contract",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="budget_analytic.type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    detail_ids = fields.One2many(
        string="Details",
        comodel_name="budget_analytic.budget_detail",
        inverse_name="budget_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    detail_revenue_ids = fields.One2many(
        string="Detail Revenue",
        comodel_name="budget_analytic.budget_detail",
        inverse_name="budget_id",
        domain=[
            ("direction", "=", "revenue"),
        ],
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    detail_cost_ids = fields.One2many(
        string="Detail Cost",
        comodel_name="budget_analytic.budget_detail",
        inverse_name="budget_id",
        domain=[
            ("direction", "=", "cost"),
        ],
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    realization_ids = fields.One2many(
        string="Realization Lines",
        comodel_name="budget_analytic.budget_realization",
        inverse_name="budget_id",
        readonly=True,
    )
    budgeted_realization_ids = fields.One2many(
        string="Budgeted Realization",
        comodel_name="budget_analytic.budget_realization_budgeted",
        inverse_name="budget_id",
        readonly=True,
    )
    unbudgeted_realization_ids = fields.One2many(
        string="Unbudgeted Realization",
        comodel_name="budget_analytic.budget_realization_unbudgeted",
        inverse_name="budget_id",
        readonly=True,
    )

    @api.depends(
        "detail_ids",
        "detail_ids.amount_subtotal",
        "analytic_account_id.line_ids",
        "analytic_account_id.line_ids.amount",
        "analytic_account_id.line_ids.unit_amount",
        "analytic_account_id.line_ids.account_id",
        "analytic_account_id.line_ids.product_uom_id",
        "analytic_account_id.line_ids.general_account_id",
        "analytic_account_id.line_ids.move_id",
    )
    @api.multi
    def _compute_amount(self):
        for document in self:
            amount_planned = amount_realized = amount_diff = 0.0
            amount_planned_revenue = (
                amount_planned_cost
            ) = (
                amount_planned_pl
            ) = (
                amount_unbudgeted_revenue_realization
            ) = (
                amount_budgeted_revenue_realization
            ) = (
                amount_revenue_realization
            ) = (
                amount_unbudgeted_cost_realization
            ) = (
                amount_budgeted_cost_realization
            ) = amount_cost_realization = amount_profit_realization = 0.0

            # Planned Computation
            for detail in document.detail_revenue_ids:
                amount_planned_revenue += detail.amount_subtotal

            for detail in document.detail_cost_ids:
                amount_planned_cost += detail.amount_subtotal

            amount_planned_pl = amount_planned_revenue - amount_planned_cost

            # Realization Computation
            for detail in document.budgeted_realization_ids.filtered(
                lambda r: r.amount_realized > 0.0
            ):
                amount_budgeted_revenue_realization += detail.amount_realized

            for detail in document.unbudgeted_realization_ids.filtered(
                lambda r: r.amount_realized > 0.0
            ):
                amount_unbudgeted_revenue_realization += detail.amount_realized

            amount_revenue_realization = (
                amount_unbudgeted_revenue_realization
                + amount_budgeted_revenue_realization
            )

            for detail in document.budgeted_realization_ids.filtered(
                lambda r: r.amount_realized < 0.0
            ):
                amount_budgeted_cost_realization += abs(detail.amount_realized)

            for detail in document.unbudgeted_realization_ids.filtered(
                lambda r: r.amount_realized < 0.0
            ):
                amount_unbudgeted_cost_realization += abs(detail.amount_realized)

            amount_cost_realization = (
                amount_unbudgeted_cost_realization + amount_budgeted_cost_realization
            )

            amount_profit_realization = (
                amount_revenue_realization - amount_cost_realization
            )

            amount_diff = amount_planned - amount_realized

            document.amount_planned = amount_planned
            document.amount_realized = amount_realized
            document.amount_diff = amount_diff

            document.amount_planned_revenue = amount_planned_revenue
            document.amount_planned_cost = amount_planned_cost
            document.amount_planned_pl = amount_planned_pl
            document.amount_unbudgeted_revenue_realization = (
                amount_unbudgeted_revenue_realization
            )
            document.amount_budgeted_revenue_realization = (
                amount_budgeted_revenue_realization
            )
            document.amount_revenue_realization = amount_revenue_realization
            document.amount_unbudgeted_cost_realization = (
                amount_unbudgeted_cost_realization
            )
            document.amount_budgeted_cost_realization = amount_budgeted_cost_realization
            document.amount_cost_realization = amount_cost_realization
            document.amount_profit_realization = amount_profit_realization

    amount_planned_revenue = fields.Float(
        string="Planned Revenue",
        compute="_compute_amount",
        store=True,
    )
    amount_planned_cost = fields.Float(
        string="Planned Cost",
        compute="_compute_amount",
        store=True,
    )
    amount_planned_pl = fields.Float(
        string="Planned Profit/Loss",
        compute="_compute_amount",
        store=True,
    )
    amount_unbudgeted_revenue_realization = fields.Float(
        string="Unbudgeted Revenue Realization",
        compute="_compute_amount",
        store=True,
    )
    amount_budgeted_revenue_realization = fields.Float(
        string="Budgeted Revenue Realization",
        compute="_compute_amount",
        store=True,
    )
    amount_revenue_realization = fields.Float(
        string="Revenue Realization",
        compute="_compute_amount",
        store=True,
    )
    amount_unbudgeted_cost_realization = fields.Float(
        string="Unbudgeted Cost Realization",
        compute="_compute_amount",
        store=True,
    )
    amount_budgeted_cost_realization = fields.Float(
        string="Budgeted Cost Realization",
        compute="_compute_amount",
        store=True,
    )
    amount_cost_realization = fields.Float(
        string="Cost Realization",
        compute="_compute_amount",
        store=True,
    )
    amount_profit_realization = fields.Float(
        string="Profit/Loss Realization",
        compute="_compute_amount",
        store=True,
    )
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
        string="State",
        default="draft",
        required=True,
        readonly=True,
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("valid", "Valid"),
            ("cancel", "Cancel"),
        ],
    )
    # Policy Field
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    restart_approval_ok = fields.Boolean(
        string="Can Restart Approval",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )
    # Log Fields
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
    )
    confirm_user_id = fields.Many2one(
        string="Confirmed By",
        comodel_name="res.users",
        readonly=True,
    )
    cancel_date = fields.Datetime(
        string="Cancel Date",
        readonly=True,
    )
    cancel_user_id = fields.Many2one(
        string="Cancelled By",
        comodel_name="res.users",
        readonly=True,
    )

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())
            document.request_validation()

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())

    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())
            document.restart_validation()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": "confirm",
            "confirm_date": fields.Datetime.now(),
            "confirm_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        sequence = self._create_sequence()
        return {
            "name": sequence,
            "state": "valid",
            "approve_date": fields.Datetime.now(),
            "approve_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "approve_date": False,
            "approve_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
        }

    @api.constrains(
        "analytic_account_id",
        "state",
    )
    def _constrains_no_duplicate_analytic_account(self):
        error_msg = _("No duplicate analytic account")
        for record in self:
            if record.state in ["confirm", "valid"]:
                criteria = [
                    ("analytic_account_id", "=", record.analytic_account_id.id),
                    ("id", "!=", record.id),
                    ("state", "in", ["confirm", "valid"]),
                ]
                count_duplicate = self.search_count(criteria)
                if count_duplicate > 0:
                    raise UserError(error_msg)

    @api.multi
    def unlink(self):
        _super = super(BudgetAnalyticBudget, self)
        force_unlink = self._context.get("force_unlink", False)
        for document in self:
            if document.state != "draft" or document.name != "/" and not force_unlink:
                msg_warning = _(
                    "You can only delete data with draft state "
                    "and name is equal to '/'"
                )
                raise UserError(msg_warning)
        _super.unlink()

    @api.multi
    def validate_tier(self):
        _super = super(BudgetAnalyticBudget, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_approve()

    @api.multi
    def restart_validation(self):
        _super = super(BudgetAnalyticBudget, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()

    @api.multi
    def name_get(self):
        result = []
        for document in self:
            if document.name == "/":
                name = "*" + str(document.id)
            else:
                name = document.name
            result.append((document.id, name))
        return result
