# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetAnalyticBudgetRealizationUnbudgetedHelper(models.Model):
    _name = "budget_analytic.budget_realization_unbudgeted_helper"
    _description = "Analytic Budget Unbudgeted Realization Helper"
    _auto = False

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="budget_analytic.budget",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
    )

    def _select_one(self):
        select_str = """
        SELECT  a.budget_id,
                a.analytic_account_id,
                a.account_id,
                a.product_id
        """
        return select_str

    def _from_one(self):
        from_str = """
        budget_analytic_budget_realization AS a
        """
        return from_str

    def _where_one(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join_one(self):
        join_str = """
        """
        return join_str

    def _group_by_one(self):
        group_str = """
        """
        return group_str

    def _select_two(self):
        select_str = """
        SELECT  b.budget_id,
                b.analytic_account_id,
                b.account_id,
                b.product_id
        """
        return select_str

    def _from_two(self):
        from_str = """
        budget_analytic_budget_realization_budgeted AS b
        """
        return from_str

    def _where_two(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join_two(self):
        join_str = """
        """
        return join_str

    def _group_by_two(self):
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
            EXCEPT
            %s
            FROM %s
            %s
        )"""
            % (
                self._table,
                self._select_one(),
                self._from_one(),
                self._where_one(),
                self._select_two(),
                self._from_two(),
                self._where_two(),
            )
        )
