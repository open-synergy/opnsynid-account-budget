# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetSummary(models.Model):
    _name = "budget.summary"
    _description = "Budget Summary"
    _auto = False

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="budget.budget",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    amount_planned = fields.Float(
        string="Planned Amount",
    )
    amount_realized = fields.Float(
        string="Realized Amount",
    )
    amount_diff = fields.Float(
        string="Diff. Amount",
    )

    def _select(self):
        select_str = """
        SELECT
            a.id AS id,
            a.budget_id AS budget_id,
            a.account_id AS account_id,
            CASE
                WHEN
                    b.amount IS NOT NULL
                THEN
                    b.amount
                ELSE 0.0 END AS amount_planned,
            CASE
                WHEN
                    c.amount IS NOT NULL
                THEN
                    c.amount
                ELSE 0.0 END AS amount_realized,
            (
            CASE
                WHEN
                    b.amount IS NOT NULL
                THEN
                    b.amount ELSE 0.0 END -
            CASE
                WHEN
                c.amount IS NOT NULL
            THEN
                c.amount ELSE 0.0 END
            ) AS amount_diff
        """
        return select_str

    def _from(self):
        from_str = """
        budget_account AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join(self):
        join_str = """
        LEFT JOIN budget_detail_summary AS b ON  a.budget_id = b.budget_id AND
                                            a.account_id = b.account_id
        LEFT JOIN budget_move_line_summary AS c ON
            a.budget_id = c.budget_id AND
            a.account_id = c.account_id
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
