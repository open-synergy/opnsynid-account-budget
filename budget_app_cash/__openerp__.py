# -*- coding: utf-8 -*-
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Budget Management - Cash",
    "version": "8.0.1.5.1",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "budget_app",
        "account_cash_flow_code",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/budget_budget_views.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
