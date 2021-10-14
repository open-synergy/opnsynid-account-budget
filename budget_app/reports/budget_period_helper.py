# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetPeriodHelper(models.Model):
    _name = "budget.period_helper"
    _description = "Budget Report Helper Per Period"
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
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    version_id = fields.Many2one(
        string="Version",
        comodel_name="budget.version",
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
    )

    def _select(self):
        select_str = """
        SELECT
            ROW_NUMBER() OVER() AS id,
            a.account_id AS account_id,
            a.company_id AS company_id,
            a.version_id AS version_id,
            a.period_id AS period_id,
            SUM(a.amount_plan) AS amount_plan,
            SUM(a.amount_realized) AS amount_realized,
            SUM(a.amount_diff) AS amount_diff
        """
        return select_str

    def _from(self):
        from_str = """
        budget_analysis AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1 AND
            a.state = 'valid'
        """
        return where_str

    def _join(self):
        join_str = """
        """
        return join_str

    def _group_by(self):
        group_str = """
            GROUP BY a.account_id,
            a.company_id,
            a.version_id,
            a.period_id
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
