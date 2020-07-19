# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp import tools


class BudgetDirectCashPeriodReport(models.Model):
    _name = "budget.direct_cash_period_report"
    _description = "Direct Cash Budget Report Per Period"
    _auto = False

    cash_flow_code_id = fields.Many2one(
        string="Cash Flow Code",
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
    running_amount_plan = fields.Float(
        string="Running Planned Amount",
    )
    running_amount_realized = fields.Float(
        string="Running Realized Amount",
    )
    running_amount_diff = fields.Float(
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
    date_start = fields.Date(
        string="Date Start",
    )
    date_stop = fields.Date(
        string="Date Stop",
    )

    def _select(self):
        select_str = """
        SELECT
            ROW_NUMBER() OVER() AS id,
            a.cash_flow_code_id AS cash_flow_code_id,
            a.company_id AS company_id,
            a.version_id AS version_id,
            a.period_id AS period_id,
            b.date_start AS date_start,
            b.date_stop AS date_stop,
            a.amount_plan AS amount_plan,
            a.amount_realized AS amount_realized,
            a.amount_diff AS amount_diff,
            SUM(a.amount_plan) OVER (
                PARTITION BY    a.cash_flow_code_id,
                                a.company_id,
                                a.version_id,
                                b.fiscalyear_id
                ORDER BY b.date_stop) AS running_amount_plan,
            SUM(a.amount_realized) OVER (
                PARTITION BY    a.cash_flow_code_id,
                                a.company_id,
                                a.version_id,
                                b.fiscalyear_id
                ORDER BY b.date_stop) AS running_amount_realized,
            SUM(a.amount_diff) OVER (
                PARTITION BY    a.cash_flow_code_id,
                                a.company_id,
                                a.version_id,
                                b.fiscalyear_id
                ORDER BY b.date_stop) AS running_amount_diff
        """
        return select_str

    def _from(self):
        from_str = """
        budget_direct_cash_period_helper AS a
        """
        return from_str

    def _where(self):
        where_str = """
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN account_period AS b ON a.period_id = b.id
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
