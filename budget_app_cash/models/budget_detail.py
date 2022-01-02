# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class BudgetDetail(models.Model):
    _name = "budget.detail"
    _inherit = "budget.detail"

    @api.depends(
        "cash_ids",
        "cash_ids.amount",
    )
    @api.multi
    def _compute_amount_cash(self):
        for document in self:
            total = 0.0
            for cash in document.cash_ids:
                total += cash.amount
            document.amount_cash = total

    amount_cash = fields.Float(
        string="Amount Cash",
        compute="_compute_amount_cash",
        store=True,
    )

    cash_ids = fields.One2many(
        string="Cash Realization",
        comodel_name="budget.detail_cash",
        inverse_name="detail_id",
        copy=True,
    )
