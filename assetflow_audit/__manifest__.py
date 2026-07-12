{
    'name': 'AssetFlow Audit',
    'version': '1.0',
    'category': 'Asset Management',
    'summary': 'Asset audit cycles and discrepancy tracking',
    'depends': ['assetflow_base', 'assetflow_asset', 'assetflow_notification'],
    'data': [
        'security/ir.model.access.csv',
        'security/audit_rules.xml',
        'views/audit_cycle_views.xml',
        'views/audit_line_views.xml',
        'views/audit_menus.xml',
        'wizards/audit_line_generate_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
