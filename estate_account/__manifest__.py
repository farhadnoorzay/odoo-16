# -*- coding: utf-8 -*-
{
    'name': "estate_account",

    'summary': """
    estate_account
    """,

    'description': """
        estate_account    
        """,

    'author': "Netlinks Ltd",
    'website': "https://www.netlinks.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['estate_property', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/estate_poperty_view.xml',
        'views/account_move_inherit_view.xml',
    ],
    # only loaded in demonstration mode
}