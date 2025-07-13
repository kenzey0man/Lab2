# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Patient Fields
    is_patient = fields.Boolean('Is Patient', default=False)
    patient_id = fields.Char('Patient ID', readonly=True, copy=False, index=True)
    date_of_birth = fields.Date('Date of Birth')
    age_display = fields.Char('Age', compute='_compute_age_display', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender')
    patient_notes = fields.Text('Patient Notes')
    
    # Doctor Fields
    is_doctor = fields.Boolean('Is Doctor', default=False)
    doctor_id = fields.Char('Doctor ID', readonly=True, copy=False, index=True)
    specialization = fields.Char('Specialization')
    license_number = fields.Char('License Number')
    
    # Relationship Fields
    lab_invoice_ids = fields.One2many('account.move', 'patient_id', string='Lab Invoices', 
                                      domain=[('is_lab_invoice', '=', True)])
    lab_invoice_count = fields.Integer('Invoice Count', compute='_compute_invoice_count')
    referred_invoice_ids = fields.One2many('account.move', 'referring_doctor_id', 
                                          string='Referred Invoices', 
                                          domain=[('is_lab_invoice', '=', True)])
    referred_invoice_count = fields.Integer('Referred Count', compute='_compute_referred_count')

    @api.model
    def create(self, vals):
        """Generate unique IDs for patients and doctors"""
        if vals.get('is_patient') and not vals.get('patient_id'):
            vals['patient_id'] = self.env['ir.sequence'].next_by_code('medical.patient.id') or '/'
        if vals.get('is_doctor') and not vals.get('doctor_id'):
            vals['doctor_id'] = self.env['ir.sequence'].next_by_code('medical.doctor.id') or '/'
        return super(ResPartner, self).create(vals)

    @api.depends('date_of_birth')
    def _compute_age_display(self):
        """Calculate and format age display based on date of birth"""
        today = date.today()
        for partner in self:
            if partner.date_of_birth:
                delta = relativedelta(today, partner.date_of_birth)
                
                # Format age based on the duration
                if delta.years > 0:
                    partner.age_display = f"{delta.years} Year{'s' if delta.years > 1 else ''}"
                elif delta.months > 0:
                    partner.age_display = f"{delta.months} Month{'s' if delta.months > 1 else ''}"
                elif delta.days > 0:
                    partner.age_display = f"{delta.days} Day{'s' if delta.days > 1 else ''}"
                else:
                    partner.age_display = "0 Days"
            else:
                partner.age_display = False

    @api.depends('lab_invoice_ids')
    def _compute_invoice_count(self):
        """Count lab invoices for patients"""
        for partner in self:
            partner.lab_invoice_count = len(partner.lab_invoice_ids)

    @api.depends('referred_invoice_ids')
    def _compute_referred_count(self):
        """Count referred invoices for doctors"""
        for partner in self:
            partner.referred_invoice_count = len(partner.referred_invoice_ids)

    def action_view_lab_invoices(self):
        """Open lab invoices for this patient"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [
            ('patient_id', '=', self.id),
            ('is_lab_invoice', '=', True)
        ]
        action['context'] = {
            'default_patient_id': self.id,
            'default_is_lab_invoice': True,
            'default_move_type': 'out_invoice',
        }
        return action

    def action_view_referred_invoices(self):
        """Open referred invoices for this doctor"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [
            ('referring_doctor_id', '=', self.id),
            ('is_lab_invoice', '=', True)
        ]
        return action

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Enhanced search to include patient/doctor IDs"""
        if args is None:
            args = []
        
        domain = args + ['|', '|', 
                        ('name', operator, name),
                        ('patient_id', operator, name),
                        ('doctor_id', operator, name)]
        
        return self.search(domain, limit=limit).name_get()

    def name_get(self):
        """Display patient/doctor ID with name"""
        result = []
        for partner in self:
            if partner.is_patient and partner.patient_id:
                name = f"[{partner.patient_id}] {partner.name}"
            elif partner.is_doctor and partner.doctor_id:
                name = f"[{partner.doctor_id}] {partner.name}"
            else:
                name = partner.name
            result.append((partner.id, name))
        return result