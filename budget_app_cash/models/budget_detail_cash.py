# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class BudgetDetailCash(models.Model):
    _name = "budget.detail_cash"
    _description = "Budget Detail Cash Realization"

    detail_id = fields.Many2one(
        string="# Budget Detail",
        comodel_name="budget.detail",
        required=True,
        ondelete="cascade",
    )
    period_id = fields.Many2one(
        string="Period",
        comodel_name="account.period",
        required=True,
    )
    direct_cash_flow_code_id = fields.Many2one(
        string="Direct Cash Flow Code",
        comodel_name="account.cash_flow_code",
        domain=[
            ("type", "=", "direct"),
        ],
        required=True,
    )
    indirect_cash_flow_code_id = fields.Many2one(
        string="Indirect Cash Flow Code",
        comodel_name="account.cash_flow_code",
        domain=[
            ("type", "=", "indirect"),
        ],
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
        default=0.0,
    )
