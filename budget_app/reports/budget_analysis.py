# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp import tools


class BudgetAnalysis(models.Model):
    _name = "budget.analysis"
    _description = "Budget Analysis"
    _auto = False

    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    amount_plan = fields.Float(
        string="Planned Amount",
    )
    amount_realized = fields.Float(
        string="Realized Amount",
    )
    amount_diff = fields.Float(
        string="Diff. Amount",
    )
    budget_id = fields.Many2one(
        string="Budget",
        comodel_name="budget.budget",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    user_id = fields.Many2one(
        string="User",
        comodel_name="res.users",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="budget.type",
    )
    version_id = fields.Many2one(
        string="Version",
        comodel_name="budget.version",
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
    )
    date_start = fields.Date(
        string="Date Start",
    )
    date_stop = fields.Date(
        string="Date Stop",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("valid", "Valid"),
            ("cancel", "Cancel"),
        ],
    )

    def _select(self):
        select_str = """
        SELECT
            a.id AS id,
            a.account_id AS account_id,
            CASE
                WHEN c.mode = 'revenue' THEN a.amount_planned
                ELSE -1.0 * a.amount_planned
            END as amount_plan,
            CASE
                WHEN c.mode = 'revenue' THEN a.amount_realized
                ELSE -1.0 * a.amount_realized
            END as amount_realized,
            a.amount_diff AS amount_diff,
            b.id AS budget_id,
            b.company_id AS company_id,
            b.user_id AS user_id,
            b.type_id AS type_id,
            b.version_id AS version_id,
            b.period_id AS period_id,
            d.date_start AS date_start,
            d.date_stop AS date_stop,
            b.state AS state
        """
        return select_str

    def _from(self):
        from_str = """
        budget_summary AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN budget_budget AS b ON a.budget_id = b.id
        JOIN budget_type AS c ON b.type_id = c.id
        JOIN account_period AS d ON b.period_id = d.id
        """
        return join_str

    def _group_by(self):
        group_str = """
        """
        return group_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        # pylint: disable=locally-disabled, sql-injection
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            %s
            %s
            %s
        )""" % (
            self._table,
            self._select(),
            self._from(),
            self._join(),
            self._where(),
            self._group_by()
        ))
