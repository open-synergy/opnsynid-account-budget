# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetCashAnalysis(models.Model):
    _name = "budget.cash_analysis"
    _description = "Budget Cash Analysis"
    _auto = False

    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    direct_cash_flow_code_id = fields.Many2one(
        string="Direct Cash Flow Code",
        comodel_name="account.cash_flow_code",
    )
    indirect_cash_flow_code_id = fields.Many2one(
        string="Indirect Cash Flow Code",
        comodel_name="account.cash_flow_code",
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
            b.account_id AS account_id,
            a.direct_cash_flow_code_id AS direct_cash_flow_code_id,
            a.indirect_cash_flow_code_id AS indirect_cash_flow_code_id,
            CASE
                WHEN d.mode = 'revenue' THEN
                    CAST(a.amount AS DOUBLE PRECISION)
                ELSE
                    CAST((0.0 - a.amount) AS DOUBLE PRECISION)
            END as amount_plan,
            0.0 AS amount_realized,
            0.0 AS amount_diff,
            c.id AS budget_id,
            c.company_id AS company_id,
            c.user_id AS user_id,
            c.type_id AS type_id,
            c.version_id AS version_id,
            a.period_id AS period_id,
            e.date_start AS date_start,
            e.date_stop AS date_stop,
            i.date_start AS previous_date_start,
            i.date_stop AS previous_date_stop,
            i.id AS previous_period_id,
            k.date_start AS next_date_start,
            k.date_stop AS next_date_stop,
            k.id AS next_period_id,
            c.state AS state
        """
        return select_str

    def _from(self):
        from_str = """
        budget_detail_cash AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN budget_detail AS b ON a.detail_id = b.id
        JOIN budget_budget AS c ON b.budget_id = c.id
        JOIN budget_type AS d ON c.type_id = d.id
        JOIN account_period AS e ON a.period_id = e.id
        JOIN account_cash_flow_code AS f ON a.direct_cash_flow_code_id = f.id
        JOIN account_cash_flow_code AS g ON a.indirect_cash_flow_code_id = g.id
        JOIN (
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY date_start DESC, date_stop DESC
                ) AS sequence,
                h1.id,
                h1.date_start,
                h1.date_stop
                FROM account_period AS h1
                WHERE h1.special IS FALSE
        ) AS h ON e.id = h.id
        LEFT JOIN (
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY date_start DESC, date_stop DESC
                ) AS sequence,
                i1.id,
                i1.date_start,
                i1.date_stop
                FROM account_period AS i1
                WHERE i1.special IS FALSE
        ) AS i ON i.sequence = (h.sequence + 1)
        JOIN (
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY date_start DESC, date_stop DESC
                ) AS sequence,
                j1.id,
                j1.date_start,
                j1.date_stop
                FROM account_period AS j1
                WHERE j1.special IS FALSE
        ) AS j ON e.id = j.id
        LEFT JOIN (
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY date_start DESC, date_stop DESC
                ) AS sequence,
                k1.id,
                k1.date_start,
                k1.date_stop
                FROM account_period AS k1
                WHERE k1.special IS FALSE
        ) AS k ON k.sequence = (j.sequence - 1)
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
