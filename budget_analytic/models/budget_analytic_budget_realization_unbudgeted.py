# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetAnalyticBudgetRealizationUnbudgeted(models.Model):
    _name = "budget_analytic.budget_realization_unbudgeted"
    _description = "Analytic Budget Unbudgeted Realization"
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
    amount_realized = fields.Float(
        string="Amount Realized",
    )

    def _select(self):
        select_str = """
        SELECT
            row_number() OVER() as id,
            a.budget_id AS budget_id,
            a.analytic_account_id AS analytic_account_id,
            a.account_id AS account_id,
            a.product_id,
            b.amount_realized AS amount_realized
        """
        return select_str

    def _from(self):
        from_str = """
        budget_analytic_budget_realization_unbudgeted_helper AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN budget_analytic_budget_realization AS b ON
            a.analytic_account_id = b.analytic_account_id AND
            a.account_id = b.account_id AND
            COALESCE(a.product_id, 0) = COALESCE(b.product_id, 0) AND
            a.budget_id = b.budget_id
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
