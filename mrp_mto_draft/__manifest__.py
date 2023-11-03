# -*- coding: utf-8 -*-
{
    'name': 'MRP MTO Draft',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Sale MRP related customizations for MRP MTO Draft',
    'description': 'This module holds Sale MRP related customizations for MRP MTO Draft.',
    'author': 'ERPGAP',
    'website': 'https://www.erpgap.com',
    'maintainer': 'ERPGAP',
    'license': 'LGPL-3',
    'depends': [
        'sale_management', 'mrp', 'sale_stock', 'sale_product_matrix'
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/mrp_production_views.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
