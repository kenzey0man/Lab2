# -*- coding: utf-8 -*-
{
    'name': 'Medical Lab Management',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Complete Medical Laboratory Management System',
    'description': """
Medical Lab Management System
=============================

This module provides comprehensive laboratory management features including:

* Patient Registration and Management
* Doctor/Referral Management  
* Lab Test Configuration
* Invoice Generation with Payment Tracking
* Sample Collection Workflow
* Diagnosis Result Entry
* Report Generation and Printing
* Barcode Integration
* Department-wise Organization
* Multi-price List Support

Main Features:
--------------
* Extends res.partner for Patient and Doctor management
* Extends account.move for Lab Invoice management
* Complete workflow from registration to result delivery
* Multiple report formats (Worksheet, Barcode, Receipt, Results)
* Role-based access control
* Integration with Odoo's accounting module

Workflow:
---------
Patient Registration → Invoice Creation → Sample Collection → 
Diagnosis → Printing → Signature → Completion
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'account',
        'sale',
        'stock',
        'web',
        'report',
        'barcodes',
    ],
    'data': [
        # Security
        'security/medical_lab_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/medical_lab_sequence.xml',
        'data/report_paperformat.xml',
        
        # Views
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/medical_lab_test_views.xml',
        'views/medical_lab_test_request_views.xml',
        'views/medical_lab_category_views.xml',
        'views/medical_lab_department_views.xml',
        'views/medical_lab_machine_views.xml',
        'views/medical_lab_menus.xml',
        
        # Reports
        'reports/worksheet_report.xml',
        'reports/barcode_report.xml',
        'reports/receipt_report.xml',
        'reports/test_result_report.xml',
        
        # Wizards
        'wizard/sample_collection_wizard_view.xml',
    ],
    'demo': [
        'demo/medical_lab_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'medical_lab_management/static/src/scss/medical_lab.scss',
            'medical_lab_management/static/src/js/medical_lab_dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}