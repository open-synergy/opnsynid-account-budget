# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetPeriodReport(models.Model):
    _name = "budget.period_report"
    _description = "Budget Report Per Period"
    _auto = False

    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
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
    previous_period_id = fields.Many2one(
        string="Previous Period",
        comodel_name="account.period",
    )
    previous_date_start = fields.Date(
        string="Previous Date Start",
    )
    previous_date_stop = fields.Date(
        string="Previous Date Stop",
    )
    next_period_id = fields.Many2one(
        string="Next Period",
        comodel_name="account.period",
    )
    next_date_start = fields.Date(
        string="Next Date Start",
    )
    next_date_stop = fields.Date(
        string="Next Date Stop",
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
    running_amount_plan = fields.Float(
        string="Running Planned Amount",
    )
    running_amount_realized = fields.Float(
        string="Running Realized Amount",
    )
    running_amount_diff = fields.Float(
        string="Diff. Amount",
    )

    def _select(self):
        select_str = """
        SELECT
            a.id AS id,
            a.account_id AS account_id,
            a.version_id AS version_id,
            a.period_id AS period_id,
            b.date_start AS date_start,
            b.date_stop AS date_stop,
            a.previous_period_id AS previous_period_id,
            a.previous_date_start AS previous_date_start,
            a.previous_date_start AS previous_date_stop,
            a.next_period_id AS next_period_id,
            a.next_date_start AS next_date_start,
            a.next_date_stop AS next_date_stop,
            COALESCE(c.amount_plan, 0.0) AS amount_plan,
            COALESCE(c.amount_realized, 0.0) AS amount_realized,
            COALESCE(c.amount_diff, 0.0) AS amount_diff,
            COALESCE(
                SUM(c.amount_plan) OVER (
                    PARTITION BY    a.account_id,
                                    a.version_id,
                                    b.fiscalyear_id
                    ORDER BY a.date_stop),
                0.0
            ) AS running_amount_plan,
            COALESCE(
                SUM(c.amount_realized) OVER (
                    PARTITION BY    a.account_id,
                                    a.version_id,
                                    b.fiscalyear_id
                    ORDER BY a.date_stop),
                0.0
            ) AS running_amount_realized,
            COALESCE(
                SUM(c.amount_diff) OVER (
                    PARTITION BY    a.account_id,
                                    a.version_id,
                                    b.fiscalyear_id
                    ORDER BY a.date_stop),
                0.0
            ) AS running_amount_diff
        """
        return select_str

    def _from(self):
        from_str = """
        budget_period_helper_header AS a
        """
        return from_str

    def _where(self):
        where_str = """
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN account_period AS b ON a.period_id = b.id
        LEFT JOIN budget_period_helper AS c ON
            a.account_id = c.account_id AND
            a.version_id = c.version_id AND
            a.period_id = c.period_id

        """
        return join_str

    def _group_by(self):
        group_str = """
        """
        return group_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        # pylint: disable=locally-disabled, sql-injection
        cr.execute(
            """CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            %s
            %s
            %s
        )"""
            % (
                self._table,
                self._select(),
                self._from(),
                self._join(),
                self._where(),
                self._group_by(),
            )
        )
