# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import barcode
from barcode.writer import ImageWriter
import base64
from io import BytesIO


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Lab Invoice Fields
    is_lab_invoice = fields.Boolean('Is Lab Invoice', default=False)
    patient_id = fields.Many2one('res.partner', string='Patient', 
                                domain=[('is_patient', '=', True)],
                                states={'draft': [('readonly', False)]})
    referring_doctor_id = fields.Many2one('res.partner', string='Referring Doctor',
                                         domain=[('is_doctor', '=', True)],
                                         states={'draft': [('readonly', False)]})
    barcode_id = fields.Char('Barcode ID', readonly=True, copy=False, index=True)
    barcode_image = fields.Binary('Barcode Image', compute='_compute_barcode_image')
    visit_notes = fields.Text('Visit Notes')
    
    # Test Management
    lab_test_ids = fields.One2many('medical.lab.test.request', 'invoice_id', 
                                  string='Lab Tests', copy=True,
                                  states={'draft': [('readonly', False)]})
    
    # Workflow Status
    sample_status = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('sample_collected', 'Sample Collected'),
        ('in_diagnosis', 'In Diagnosis'),
        ('ready_to_print', 'Ready to Print'),
        ('printed', 'Printed'),
        ('signed', 'Signed'),
        ('done', 'Done')
    ], string='Lab Status', default='draft', tracking=True)
    
    # Tracking Fields
    worksheet_printed = fields.Boolean('Worksheet Printed', default=False)
    barcode_printed = fields.Boolean('Barcode Printed', default=False)
    result_printed = fields.Boolean('Result Printed', default=False)
    
    # Additional Info
    sample_collection_time = fields.Datetime('Sample Collection Time')
    expected_delivery_date = fields.Date('Expected Delivery Date')
    actual_delivery_date = fields.Date('Actual Delivery Date')

    @api.model
    def create(self, vals):
        """Generate barcode ID for lab invoices"""
        if vals.get('is_lab_invoice') and not vals.get('barcode_id'):
            vals['barcode_id'] = self.env['ir.sequence'].next_by_code('medical.lab.barcode') or '/'
        return super(AccountMove, self).create(vals)

    @api.depends('barcode_id')
    def _compute_barcode_image(self):
        """Generate barcode image from barcode ID"""
        for move in self:
            if move.barcode_id and move.barcode_id != '/':
                try:
                    # Generate Code128 barcode
                    code128 = barcode.get('code128', move.barcode_id, writer=ImageWriter())
                    buffer = BytesIO()
                    code128.write(buffer)
                    buffer.seek(0)
                    move.barcode_image = base64.b64encode(buffer.read())
                except Exception:
                    move.barcode_image = False
            else:
                move.barcode_image = False

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """Auto-fill patient information"""
        if self.patient_id:
            self.partner_id = self.patient_id

    def action_post(self):
        """Override to update lab status when invoice is posted"""
        res = super(AccountMove, self).action_post()
        for move in self.filtered('is_lab_invoice'):
            if move.sample_status == 'draft':
                move.sample_status = 'invoiced'
        return res

    def action_update_sample_collected(self):
        """Mark sample as collected"""
        self.ensure_one()
        if self.sample_status != 'invoiced':
            raise ValidationError("Sample can only be collected after invoicing.")
        
        self.write({
            'sample_status': 'sample_collected',
            'sample_collection_time': fields.Datetime.now()
        })
        
        # Update all test requests
        self.lab_test_ids.write({'status': 'collected'})

    def action_start_diagnosis(self):
        """Start diagnosis process"""
        self.ensure_one()
        if self.sample_status != 'sample_collected':
            raise ValidationError("Cannot start diagnosis before sample collection.")
        
        self.sample_status = 'in_diagnosis'
        self.lab_test_ids.write({'status': 'in_progress'})

    def action_ready_to_print(self):
        """Mark as ready to print"""
        self.ensure_one()
        if not all(test.status == 'completed' for test in self.lab_test_ids):
            raise ValidationError("All tests must be completed before printing.")
        
        self.sample_status = 'ready_to_print'

    def action_mark_printed(self):
        """Mark results as printed"""
        self.ensure_one()
        self.write({
            'sample_status': 'printed',
            'result_printed': True
        })
        self.lab_test_ids.write({'status': 'printed'})

    def action_mark_signed(self):
        """Mark results as signed"""
        self.ensure_one()
        self.sample_status = 'signed'

    def action_mark_done(self):
        """Mark process as complete"""
        self.ensure_one()
        self.write({
            'sample_status': 'done',
            'actual_delivery_date': fields.Date.today()
        })

    def action_print_worksheet(self):
        """Print lab worksheet"""
        self.ensure_one()
        self.worksheet_printed = True
        return self.env.ref('medical_lab_management.action_report_lab_worksheet').report_action(self)

    def action_print_barcode(self):
        """Print barcode sticker"""
        self.ensure_one()
        self.barcode_printed = True
        return self.env.ref('medical_lab_management.action_report_lab_barcode').report_action(self)

    def action_print_receipt(self):
        """Print payment receipt"""
        self.ensure_one()
        return self.env.ref('medical_lab_management.action_report_lab_receipt').report_action(self)

    def action_print_results(self):
        """Print test results"""
        self.ensure_one()
        if self.sample_status not in ['ready_to_print', 'printed', 'signed', 'done']:
            raise ValidationError("Results can only be printed when ready.")
        return self.env.ref('medical_lab_management.action_report_lab_results').report_action(self)

    @api.model
    def get_lab_dashboard_data(self):
        """Get dashboard statistics for lab management"""
        today = fields.Date.today()
        
        # Today's statistics
        today_invoices = self.search_count([
            ('is_lab_invoice', '=', True),
            ('invoice_date', '=', today)
        ])
        
        # Status wise count
        status_data = {}
        for status, label in self._fields['sample_status'].selection:
            count = self.search_count([
                ('is_lab_invoice', '=', True),
                ('sample_status', '=', status)
            ])
            status_data[status] = {'label': label, 'count': count}
        
        # Financial summary
        total_due = sum(self.search([
            ('is_lab_invoice', '=', True),
            ('payment_state', '!=', 'paid'),
            ('state', '=', 'posted')
        ]).mapped('amount_residual'))
        
        return {
            'today_count': today_invoices,
            'status_summary': status_data,
            'total_due': total_due,
        }