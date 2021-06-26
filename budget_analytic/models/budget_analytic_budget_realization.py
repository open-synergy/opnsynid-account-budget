# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, tools


class BudgetAnalyticBudgetRealization(models.Model):
    _name = "budget_analytic.budget_realization"
    _description = "Analytic Budget Realization"
    _auto = False

    budget_id = fields.Many2one(
        string="# Budget",
        comodel_name="budget_analytic.budget",
    )
    analytic_account_id = fields.Many2one(
        string="Account",
        comodel_name="account.analytic.account",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
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
        SELECT  row_number() OVER() as id,
                a.id AS budget_id,
                b.account_id AS analytic_account_id,
                b.general_account_id AS account_id,
                b.product_id AS product_id,
                b.amount AS amount_realized
        """
        return select_str

    def _from(self):
        from_str = """
        budget_analytic_budget AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN (
            SELECT  b1.account_id,
                    b1.general_account_id,
                    b1.product_id,
                    SUM(b1.amount) AS amount
            FROM account_analytic_line AS b1
            WHERE       b1.move_id IS NOT NULL
            GROUP BY    b1.account_id,
                        b1.general_account_id,
                        b1.product_id

        ) AS b ON   a.analytic_account_id = b.account_id
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
