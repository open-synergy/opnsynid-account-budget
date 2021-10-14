# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetPeriodHelperHeader(models.Model):
    _name = "budget.period_helper_header"
    _description = "Budget Report Per Period - Header Helper"
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

    def _select(self):
        select_str = """
        SELECT
            ROW_NUMBER() OVER() AS id,
            a.id AS account_id,
            b.id AS period_id,
            c.id AS version_id,
            b.date_start AS date_start,
            b.date_stop AS date_stop,
            e.id AS previous_period_id,
            e.date_start AS previous_date_start,
            e.date_stop AS previous_date_stop,
            g.id AS next_period_id,
            g.date_start AS next_date_start,
            g.date_stop AS next_date_stop
        """
        return select_str

    def _from(self):
        from_str = """
        account_account AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE    a.type NOT IN ('view', 'consolidation', 'closed')
        """
        return where_str

    def _join(self):
        join_str = """
        CROSS JOIN    account_period AS b
        CROSS JOIN    budget_version AS c
        JOIN (
            SELECT
            ROW_NUMBER() OVER (
                ORDER BY date_start DESC, date_stop DESC
            ) AS sequence,
            d1.id,
            d1.date_start,
            d1.date_stop
            FROM account_period AS d1
            WHERE d1.special IS FALSE
        ) AS d ON d.id = b.id
        LEFT JOIN (
            SELECT
            ROW_NUMBER() OVER (
                ORDER BY date_start DESC, date_stop DESC
            ) AS sequence,
            e1.id,
            e1.date_start,
            e1.date_stop
            FROM account_period AS e1
            WHERE e1.special IS FALSE
        ) AS e ON e.sequence = (d.sequence + 1)
        JOIN (
            SELECT
            ROW_NUMBER() OVER (
                ORDER BY date_start DESC, date_stop DESC
            ) AS sequence,
            f1.id,
            f1.date_start,
            f1.date_stop
            FROM account_period AS f1
            WHERE f1.special IS FALSE
        ) AS f ON b.id = f.id
        LEFT JOIN (
            SELECT
            ROW_NUMBER() OVER (
                ORDER BY date_start DESC, date_stop DESC
            ) AS sequence,
            g1.id,
            g1.date_start,
            g1.date_stop
            FROM account_period AS g1
            WHERE g1.special IS FALSE
        ) AS g ON g.sequence = (f.sequence - 1)
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
