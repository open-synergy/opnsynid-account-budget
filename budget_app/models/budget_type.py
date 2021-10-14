# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class BudgetType(models.Model):
    _name = "budget.type"
    _description = "Budget Type"

    name = fields.Char(
        string="Budget Type",
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
    mode = fields.Selection(
        string="Mode",
        selection=[
            ("revenue", "Revenue"),
            ("expense", "Expense"),
        ],
        required=True,
        default="expense",
    )
    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    allowed_account_ids = fields.Many2many(
        string="Allowed Accounts",
        comodel_name="account.account",
        relation="rel_budget_type_2_account",
        column1="type_id",
        column2="account_id",
        domain=[("type", "not in", ["view", "consolidation", "closed"])],
    )
    budget_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Budget",
        comodel_name="res.groups",
        relation="rel_budget_type_confirm_budget",
        column1="type_id",
        column2="group_id",
    )
    budget_approve_grp_ids = fields.Many2many(
        string="Allow To Approve Budget",
        comodel_name="res.groups",
        relation="rel_budget_type_approve_budget",
        column1="type_id",
        column2="group_id",
    )
    budget_restart_approval_grp_ids = fields.Many2many(
        string="Allow To Restart Budget Approval",
        comodel_name="res.groups",
        relation="rel_budget_type_restart_approve_budget",
        column1="type_id",
        column2="group_id",
    )
    budget_approve_grp_ids = fields.Many2many(
        string="Allow To Approve Budget",
        comodel_name="res.groups",
        relation="rel_budget_type_approve_budget",
        column1="type_id",
        column2="group_id",
    )
    budget_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Budget",
        comodel_name="res.groups",
        relation="rel_budget_type_cancel_budget",
        column1="type_id",
        column2="group_id",
    )
    budget_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Budget",
        comodel_name="res.groups",
        relation="rel_budget_type_approve_budget",
        column1="type_id",
        column2="group_id",
    )
