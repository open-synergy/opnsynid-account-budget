# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetMoveLine(models.Model):
    _name = "budget.move_line"
    _description = "Budget Move Line"
    _auto = False

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="budget.budget",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )
    move_id = fields.Many2one(
        string="# Move",
        comodel_name="account.move",
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
    )
    amount = fields.Float(
        string="Amount",
    )

    def _select(self):
        select_str = """
        SELECT
            row_number() OVER() as id,
            a.id AS budget_id,
            d.account_id AS account_id,
            d.move_id AS move_id,
            d.period_id AS period_id,
            d.journal_id AS journal_id,
            CASE
                WHEN
                    g.report_type = 'asset' OR g.report_type = 'expense'
                THEN
                    (d.debit - d.credit)
                ELSE
                    (d.credit - d.debit)
            END AS amount
        """
        return select_str

    def _from(self):
        from_str = """
        budget_budget AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1 AND
        e.state = 'posted'
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN budget_type AS b ON a.type_id = b.id
        JOIN rel_budget_type_2_account AS c ON b.id = c.type_id
        JOIN account_move_line AS d ON  a.period_id = d.period_id AND
                                        c.account_id = d.account_id
        JOIN account_move AS e ON d.move_id = e.id
        JOIN account_account AS f ON d.account_id = f.id
        JOIN account_account_type AS g ON f.user_type = g.id
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
