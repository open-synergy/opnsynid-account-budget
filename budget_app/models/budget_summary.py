# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields
from openerp import tools


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
            row_number() OVER() as id,
            a.id AS budget_id,
            c.account_id AS account_id,
            CASE
                WHEN
                    d.amount IS NOT NULL
                THEN
                    d.amount
                ELSE 0.0 END AS amount_planned,
            CASE
                WHEN
                    e.amount IS NOT NULL
                THEN
                    e.amount
                ELSE 0.0 END AS amount_realized,
            (
            CASE
                WHEN
                    d.amount IS NOT NULL
                THEN
                    d.amount ELSE 0.0 END -
            CASE
                WHEN
                e.amount IS NOT NULL
            THEN
                e.amount ELSE 0.0 END
            ) AS amount_diff
        """
        return select_str

    def _from(self):
        from_str = """
        budget_budget AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN budget_type AS b ON a.type_id = b.id
        JOIN rel_budget_type_2_account AS c ON b.id = c.type_id
        LEFT JOIN budget_detail_summary AS d ON  a.id = d.budget_id AND
                                            c.account_id = d.account_id
        LEFT JOIN budget_move_line_summary AS e ON   a.id = e.budget_id AND
                                                c.account_id = e.account_id
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
