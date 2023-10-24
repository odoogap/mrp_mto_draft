# -*- coding: utf-8 -*-
{
    # App information
    'name': 'MRP MTO Draft',
    'version': '15.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Sale MRP related customizations for MRP MTO Draft',
    'description': 'This module holds Sale MRP related customizations for MRP MTO Draft.',

    # Author
    'author': 'ERPGAP',
    'website': 'https://www.erpgap.com',
    'maintainer': 'ERPGAP',
    'license': 'LGPL-3',

    # Dependencies
    'depends': [
        'sale_management', 'mrp', 'sale_stock', 'sale_product_matrix'
    ],

    # Views
    'data': [
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/mrp_production_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_mto_draft/static/src/js/product_configurator_widget.js',
        ],
    },

    # Module Specific
    'application': False,
    'installable': True,
    'auto_install': False,
}
