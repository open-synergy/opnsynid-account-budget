# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval as eval


class BudgetQuantityComputation(models.Model):
    _name = "budget.quantity_computation"
    _description = "Budget Quantity Computation"

    name = fields.Char(
        string="Quantity Computation",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    python_code = fields.Text(
        string="Python Code",
    )

    def _get_localdict(self, document):
        self.ensure_one()
        return {
            "env": self.env,
            "document": document,
        }

    @api.multi
    def _get_qty(self, document):
        self.ensure_one()
        localdict = self._get_localdict(document)
        try:
            eval(self.python_code, localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = 0.0
        return result
