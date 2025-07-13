# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from odoo.exceptions import ValidationError


class MedicalLabTest(models.Model):
    _name = 'medical.lab.test'
    _description = 'Medical Lab Test Configuration'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Test Name', required=True, tracking=True)
    code = fields.Char('Test Code', required=True, copy=False, index=True)
    shortcut = fields.Char('Shortcut', help='Quick reference code')
    unit = fields.Char('Unit of Measure')
    
    # Sample Information
    sample_type = fields.Selection([
        ('blood', 'Blood'),
        ('urine', 'Urine'),
        ('stool', 'Stool'),
        ('sputum', 'Sputum'),
        ('tissue', 'Tissue'),
        ('fluid', 'Body Fluid'),
        ('swab', 'Swab'),
        ('other', 'Other')
    ], string='Sample Type', required=True)
    sample_volume = fields.Char('Required Volume', help='e.g., 5ml, 10ml')
    
    # Categorization
    category_ids = fields.Many2many('medical.lab.test.category', 
                                   'lab_test_category_rel',
                                   'test_id', 'category_id',
                                   string='Categories')
    department_id = fields.Many2one('medical.lab.department', string='Department')
    machine_id = fields.Many2one('medical.lab.machine', string='Machine')
    
    # Pricing
    price_ids = fields.One2many('medical.lab.test.price', 'test_id', string='Price List')
    list_price = fields.Float('Standard Price', digits='Product Price')
    
    # Result Configuration
    result_type = fields.Selection([
        ('selection', 'Selection'),
        ('range', 'Range'),
        ('quantitative', 'Quantitative'),
        ('descriptive', 'Descriptive')
    ], string='Result Type', required=True, default='quantitative')
    
    # Selection Type Configuration
    selection_options = fields.Text('Selection Options', 
                                   help='JSON format: [{"value": "positive", "label": "Positive"}]')
    
    # Range Type Configuration
    normal_ranges = fields.One2many('medical.lab.test.range', 'test_id', string='Normal Ranges')
    
    # Report Configuration
    report_template = fields.Selection([
        ('table', 'Table Format'),
        ('custom', 'Custom Template')
    ], string='Report Template', default='table')
    custom_template = fields.Text('Custom Template HTML')
    
    # Other Settings
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    processing_time = fields.Integer('Processing Time (Hours)', 
                                    help='Expected time to complete the test')
    critical_values = fields.Text('Critical Values', 
                                 help='Define critical value ranges that need immediate attention')
    methodology = fields.Text('Methodology')
    clinical_significance = fields.Text('Clinical Significance')
    preparation_instructions = fields.Text('Patient Preparation Instructions')
    
    # Statistics
    test_count = fields.Integer('Total Tests', compute='_compute_test_count')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Test code must be unique!'),
    ]

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for test in self:
            name = f"[{test.code}] {test.name}" if test.code else test.name
            result.append((test.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', '|',
                        ('name', operator, name),
                        ('code', operator, name),
                        ('shortcut', operator, name)]
        return self.search(domain, limit=limit).name_get()

    def _compute_test_count(self):
        """Count total test requests for this test"""
        TestRequest = self.env['medical.lab.test.request']
        for test in self:
            test.test_count = TestRequest.search_count([('test_id', '=', test.id)])

    @api.constrains('selection_options')
    def _check_selection_options(self):
        """Validate JSON format for selection options"""
        for test in self:
            if test.result_type == 'selection' and test.selection_options:
                try:
                    options = json.loads(test.selection_options)
                    if not isinstance(options, list):
                        raise ValueError("Options must be a list")
                    for opt in options:
                        if not isinstance(opt, dict) or 'value' not in opt:
                            raise ValueError("Each option must have a 'value' key")
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValidationError(f"Invalid selection options format: {str(e)}")

    def get_selection_options(self):
        """Get parsed selection options"""
        self.ensure_one()
        if self.result_type == 'selection' and self.selection_options:
            try:
                return json.loads(self.selection_options)
            except json.JSONDecodeError:
                return []
        return []

    def get_normal_range(self, gender='all', age=None):
        """Get applicable normal range based on gender and age"""
        self.ensure_one()
        if self.result_type != 'range':
            return None
            
        # Find matching range
        for range_rec in self.normal_ranges:
            if range_rec.gender != 'all' and range_rec.gender != gender:
                continue
            if age is not None:
                if range_rec.age_from and age < range_rec.age_from:
                    continue
                if range_rec.age_to and age > range_rec.age_to:
                    continue
            return range_rec
            
        # Return first range if no specific match
        return self.normal_ranges[0] if self.normal_ranges else None

    def evaluate_result(self, value, gender='all', age=None):
        """Evaluate test result against normal ranges"""
        self.ensure_one()
        
        if self.result_type == 'range':
            normal_range = self.get_normal_range(gender, age)
            if normal_range and isinstance(value, (int, float)):
                if value < normal_range.min_value:
                    return 'low'
                elif value > normal_range.max_value:
                    return 'high'
                else:
                    return 'normal'
        
        return None

    @api.model
    def create_common_tests(self):
        """Create common lab tests - used for initial setup"""
        common_tests = [
            {
                'name': 'Complete Blood Count',
                'code': 'CBC',
                'sample_type': 'blood',
                'result_type': 'range',
                'unit': 'cells/μL',
                'list_price': 25.0,
            },
            {
                'name': 'Blood Glucose',
                'code': 'GLU',
                'sample_type': 'blood',
                'result_type': 'range',
                'unit': 'mg/dL',
                'list_price': 15.0,
            },
            {
                'name': 'COVID-19 RT-PCR',
                'code': 'COV19',
                'sample_type': 'swab',
                'result_type': 'selection',
                'selection_options': json.dumps([
                    {'value': 'positive', 'label': 'Positive'},
                    {'value': 'negative', 'label': 'Negative'},
                    {'value': 'inconclusive', 'label': 'Inconclusive'}
                ]),
                'list_price': 100.0,
            },
        ]
        
        for test_vals in common_tests:
            if not self.search([('code', '=', test_vals['code'])]):
                self.create(test_vals)