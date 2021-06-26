# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Analytic Budget Management",
    "version": "8.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "budget_app",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/base_cancel_reason_configurator_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "menu.xml",
        "views/budget_analytic_type_views.xml",
        # "views/budget_version_views.xml",
        # "views/budget_quantity_computation_views.xml",
        "views/budget_analytic_budget_views.xml",
        # "views/budget_budget_views.xml",
        # "reports/budget_analysis.xml",
    ],
    "demo": [
        # "demo/budget_type_demo.xml",
        # "demo/budget_version_demo.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
