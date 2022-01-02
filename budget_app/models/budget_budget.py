# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class BudgetBudget(models.Model):
    _name = "budget.budget"
    _description = "Budget"
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

    @api.depends(
        "detail_ids",
        "detail_ids.amount_subtotal",
    )
    @api.multi
    def _compute_amount(self):
        for document in self:
            amount_planned = amount_realized = amount_diff = 0.0
            for detail in document.detail_ids:
                amount_planned += detail.amount_subtotal

            for ml in document.move_line_ids:
                amount_realized += ml.amount

            amount_diff = amount_planned - amount_realized

            document.amount_planned = amount_planned
            document.amount_realized = amount_realized
            document.amount_diff = amount_diff

    @api.depends(
        "type_id",
    )
    @api.multi
    def _compute_allowed_account_ids(self):
        for document in self:
            document.allowed_account_ids = []
            if document.type_id:
                document.allowed_account_ids = document.type_id.allowed_account_ids

    name = fields.Char(
        string="# Budget",
        default="/",
        copy=False,
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
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
        comodel_name="budget.type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    version_id = fields.Many2one(
        string="Version",
        comodel_name="budget.version",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        compute="_compute_allowed_account_ids",
        relation="rel_budget_2_allowed_account",
        store=False,
    )
    detail_ids = fields.One2many(
        string="Details",
        comodel_name="budget.detail",
        inverse_name="budget_id",
        copy=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    detail_account_ids = fields.One2many(
        string="Detail Accounts",
        comodel_name="budget.account",
        inverse_name="budget_id",
        readonly=True,
    )
    detail_summary_ids = fields.One2many(
        string="Detail Summary",
        comodel_name="budget.detail_summary",
        inverse_name="budget_id",
        readonly=True,
    )
    move_line_ids = fields.One2many(
        string="Move Lines",
        comodel_name="budget.move_line",
        inverse_name="budget_id",
        readonly=True,
    )
    move_line_summary_ids = fields.One2many(
        string="Move Line Summary",
        comodel_name="budget.move_line_summary",
        inverse_name="budget_id",
        readonly=True,
    )
    summary_ids = fields.One2many(
        string="Budget Summary",
        comodel_name="budget.summary",
        inverse_name="budget_id",
        readonly=True,
    )
    amount_planned = fields.Float(
        string="Planned Amount",
        compute="_compute_amount",
        store=False,
    )
    amount_realized = fields.Float(
        string="Realized Amount",
        compute="_compute_amount",
        store=False,
    )
    amount_diff = fields.Float(
        string="Diff Amount",
        compute="_compute_amount",
        store=False,
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
    approve_ok = fields.Boolean(
        string="Can Approve",
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
    approve_date = fields.Datetime(
        string="Approve Date",
        readonly=True,
    )
    approve_user_id = fields.Many2one(
        string="Approve By",
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
        return {
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

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(BudgetBudget, self)
        _super.unlink()

    @api.model
    def create(self, values):
        _super = super(BudgetBudget, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )
        return result

    @api.multi
    def validate_tier(self):
        _super = super(BudgetBudget, self)
        _super.validate_tier()
        for document in self:
            if document.validated:
                document.action_approve()

    @api.multi
    def restart_validation(self):
        _super = super(BudgetBudget, self)
        _super.restart_validation()
        for document in self:
            document.request_validation()
