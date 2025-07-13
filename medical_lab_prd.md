# Medical Lab Management System - Product Requirements Document (PRD)

## 1. Overview

### 1.1 Product Name
Medical Lab Management System (MLMS)

### 1.2 Module Technical Name
`medical_lab_management`

### 1.3 Version
1.0.0

### 1.4 Odoo Version Compatibility
Odoo 15.0+ (Community & Enterprise)

### 1.5 Executive Summary
The Medical Lab Management System is an Odoo addon designed to streamline laboratory operations from patient registration through test result delivery. The system leverages Odoo's existing partner management (`res.partner`) for patients and doctors, and the invoicing module (`account.move`) for financial management.

### 1.6 Workflow Overview
```
Patient Registration → Invoice Creation → Sample Collection → Diagnosis → Printing → Signature → Completion
```

## 2. Technical Architecture

### 2.1 Module Dependencies
```python
{
    'depends': [
        'base',
        'account',
        'sale',
        'stock',
        'web',
        'report',
        'barcodes',
    ]
}
```

### 2.2 Core Models

#### 2.2.1 Patient Management
- **Model**: Extends `res.partner`
- **Fields**:
  ```python
  is_patient = fields.Boolean('Is Patient', default=False)
  patient_id = fields.Char('Patient ID', readonly=True, copy=False)
  date_of_birth = fields.Date('Date of Birth')
  age_display = fields.Char('Age', compute='_compute_age_display', store=True)
  gender = fields.Selection([
      ('male', 'Male'),
      ('female', 'Female')
  ])
  patient_notes = fields.Text('Patient Notes')
  lab_invoice_ids = fields.One2many('account.move', 'patient_id', string='Lab Invoices')
  lab_invoice_count = fields.Integer(compute='_compute_invoice_count')
  ```

#### 2.2.2 Doctor Management
- **Model**: Extends `res.partner`
- **Fields**:
  ```python
  is_doctor = fields.Boolean('Is Doctor', default=False)
  doctor_id = fields.Char('Doctor ID', readonly=True, copy=False)
  specialization = fields.Char('Specialization')
  license_number = fields.Char('License Number')
  ```

#### 2.2.3 Lab Invoice (Visit)
- **Model**: Extends `account.move`
- **Fields**:
  ```python
  is_lab_invoice = fields.Boolean('Is Lab Invoice', default=False)
  patient_id = fields.Many2one('res.partner', domain=[('is_patient', '=', True)])
  referring_doctor_id = fields.Many2one('res.partner', domain=[('is_doctor', '=', True)])
  barcode_id = fields.Char('Barcode ID', readonly=True, copy=False)
  visit_notes = fields.Text('Visit Notes')
  lab_test_ids = fields.One2many('medical.lab.test.request', 'invoice_id')
  sample_status = fields.Selection([
      ('draft', 'Draft'),
      ('invoiced', 'Invoiced'),
      ('sample_collected', 'Sample Collected'),
      ('in_diagnosis', 'In Diagnosis'),
      ('ready_to_print', 'Ready to Print'),
      ('printed', 'Printed'),
      ('signed', 'Signed'),
      ('done', 'Done')
  ], default='draft')
  worksheet_printed = fields.Boolean('Worksheet Printed')
  barcode_printed = fields.Boolean('Barcode Printed')
  ```

#### 2.2.4 Lab Test Configuration
- **Model**: `medical.lab.test`
- **Fields**:
  ```python
  name = fields.Char('Test Name', required=True)
  code = fields.Char('Test Code', required=True)
  shortcut = fields.Char('Shortcut')
  unit = fields.Char('Unit of Measure')
  sample_type = fields.Selection([
      ('blood', 'Blood'),
      ('urine', 'Urine'),
      ('stool', 'Stool'),
      ('sputum', 'Sputum'),
      ('other', 'Other')
  ])
  category_ids = fields.Many2many('medical.lab.test.category', string='Categories')
  department_id = fields.Many2one('medical.lab.department', string='Department')
  machine_id = fields.Many2one('medical.lab.machine', string='Machine')
  price_ids = fields.One2many('medical.lab.test.price', 'test_id', string='Price List')
  result_type = fields.Selection([
      ('selection', 'Selection'),
      ('range', 'Range'),
      ('quantitative', 'Quantitative'),
      ('descriptive', 'Descriptive')
  ], required=True)
  selection_options = fields.Text('Selection Options')  # JSON field
  normal_ranges = fields.One2many('medical.lab.test.range', 'test_id')
  report_template = fields.Selection([
      ('table', 'Table Format'),
      ('custom', 'Custom Template')
  ])
  sequence = fields.Integer('Sequence', default=10)
  active = fields.Boolean('Active', default=True)
  ```

#### 2.2.5 Test Request (Invoice Line)
- **Model**: `medical.lab.test.request`
- **Fields**:
  ```python
  invoice_id = fields.Many2one('account.move', required=True, ondelete='cascade')
  test_id = fields.Many2one('medical.lab.test', required=True)
  patient_id = fields.Many2one('res.partner', related='invoice_id.patient_id')
  status = fields.Selection([
      ('pending', 'Pending'),
      ('collected', 'Sample Collected'),
      ('in_progress', 'In Progress'),
      ('completed', 'Completed'),
      ('verified', 'Verified'),
      ('printed', 'Printed')
  ], default='pending')
  result_value = fields.Text('Result Value')
  result_status = fields.Selection([
      ('normal', 'Normal'),
      ('low', 'Low'),
      ('high', 'High'),
      ('critical', 'Critical')
  ])
  technician_id = fields.Many2one('res.users', string='Technician')
  doctor_id = fields.Many2one('res.users', string='Doctor')
  diagnosis_date = fields.Datetime('Diagnosis Date')
  notes = fields.Text('Notes')
  ```

#### 2.2.6 Test Categories
- **Model**: `medical.lab.test.category`
- **Fields**:
  ```python
  name = fields.Char('Category Name', required=True)
  code = fields.Char('Category Code')
  parent_id = fields.Many2one('medical.lab.test.category', string='Parent Category')
  child_ids = fields.One2many('medical.lab.test.category', 'parent_id', string='Child Categories')
  sequence = fields.Integer('Sequence', default=10)
  ```

#### 2.2.7 Departments
- **Model**: `medical.lab.department`
- **Fields**:
  ```python
  name = fields.Char('Department Name', required=True)
  code = fields.Char('Department Code')
  manager_id = fields.Many2one('res.users', string='Department Manager')
  location = fields.Char('Location')
  active = fields.Boolean('Active', default=True)
  ```

#### 2.2.8 Lab Machines
- **Model**: `medical.lab.machine`
- **Fields**:
  ```python
  name = fields.Char('Machine Name', required=True)
  model = fields.Char('Model')
  serial_number = fields.Char('Serial Number')
  department_id = fields.Many2one('medical.lab.department')
  status = fields.Selection([
      ('active', 'Active'),
      ('maintenance', 'Under Maintenance'),
      ('inactive', 'Inactive')
  ], default='active')
  ```

#### 2.2.9 Test Price List
- **Model**: `medical.lab.test.price`
- **Fields**:
  ```python
  test_id = fields.Many2one('medical.lab.test', required=True)
  pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
  price = fields.Float('Price', required=True)
  currency_id = fields.Many2one('res.currency', related='pricelist_id.currency_id')
  date_start = fields.Date('Start Date')
  date_end = fields.Date('End Date')
  ```

#### 2.2.10 Test Normal Ranges
- **Model**: `medical.lab.test.range`
- **Fields**:
  ```python
  test_id = fields.Many2one('medical.lab.test', required=True)
  gender = fields.Selection([
      ('all', 'All'),
      ('male', 'Male'),
      ('female', 'Female')
  ], default='all')
  age_from = fields.Integer('Age From (Years)')
  age_to = fields.Integer('Age To (Years)')
  min_value = fields.Float('Minimum Value')
  max_value = fields.Float('Maximum Value')
  unit = fields.Char('Unit')
  ```

## 3. User Interface Specifications

### 3.1 Menu Structure
```
Medical Lab Management/
├── Patients/
│   ├── Patients (List & Form View)
│   └── Create New Patient
├── Invoices/
│   ├── Lab Invoices (List & Form View)
│   ├── Create New Invoice
│   └── Invoice Analysis
├── Laboratory/
│   ├── Sample Collection
│   ├── Diagnosis
│   ├── Printing Queue
│   └── Completed Tests
├── Configuration/
│   ├── Tests/
│   │   ├── Test Catalog
│   │   ├── Test Categories
│   │   └── Test Packages
│   ├── Departments
│   ├── Machines
│   ├── Price Lists
│   └── Doctors
└── Reports/
    ├── Daily Collection Report
    ├── Test Statistics
    └── Financial Summary
```

### 3.2 Views

#### 3.2.1 Patient View
- **List View Fields**: Patient ID, Name, Age, Gender, Phone, Last Visit
- **Form View**:
  - Basic Information Tab
  - Medical History Tab
  - Invoice History Tab (Smart Button)
  - Notes Tab

#### 3.2.2 Invoice View
- **List View Fields**: Invoice ID, Barcode, Patient Name, Total, Paid, Due, Status, Created Date
- **Form View**:
  - Header: Status Bar
  - Patient Information Section
  - Test Selection Section
  - Financial Summary Section
  - Action Buttons: Print Worksheet, Print Barcode, Print Receipt

#### 3.2.3 Sample Collection View
- **Kanban View**: Cards showing pending samples by department
- **List View**: Filterable by status, date, department

#### 3.2.4 Diagnosis View
- **Form View**: 
  - Test details
  - Result entry fields (dynamic based on test type)
  - Technician/Doctor assignment
  - Notes section

### 3.3 Workflows

#### 3.3.1 Patient Registration Workflow
1. Search existing patient (by name/phone)
2. If not found → Create new patient
3. Auto-generate Patient ID
4. Calculate age from DOB
5. Save and navigate to invoice

#### 3.3.2 Invoice Creation Workflow
1. Select/Create patient
2. Select referring doctor
3. Add tests (with pricing)
4. Calculate totals with discounts
5. Record payment
6. Generate barcode
7. Print worksheet and barcode

#### 3.3.3 Sample Processing Workflow
1. Receive sample with worksheet
2. Scan/Enter barcode
3. Update status to "Sample Collected"
4. Route to appropriate department
5. Enter diagnosis results
6. Update status through workflow

## 4. Reports and Printing

### 4.1 Worksheet Report
- **Format**: A4 PDF
- **Content**:
  - Header: Lab name and logo
  - Patient details section
  - Test list with space for manual results
  - Barcode section
  - Footer: Technician signature area

### 4.2 Barcode Sticker
- **Format**: Label printer compatible (e.g., 50mm x 25mm)
- **Content**:
  - Barcode (Code128 or similar)
  - Patient name
  - Optional: Age, Gender
  - Collection date

### 4.3 Receipt
- **Format**: Thermal printer or A5 PDF
- **Content**:
  - Lab details
  - Invoice number
  - Patient information
  - Test list with prices
  - Payment summary
  - Terms and conditions

### 4.4 Test Result Report
- **Format**: A4 PDF
- **Layout Options**:
  - Table format
  - Grouped by category
  - Custom templates per test
- **Content**:
  - Patient demographics
  - Test results with normal ranges
  - Interpretation notes
  - Doctor/Technician signatures
  - Lab certification footer

## 5. Security and Access Control

### 5.1 User Groups
```xml
<record id="group_lab_reception" model="res.groups">
    <field name="name">Lab Reception</field>
    <field name="category_id" ref="base.module_category_medical_lab"/>
</record>

<record id="group_lab_technician" model="res.groups">
    <field name="name">Lab Technician</field>
    <field name="category_id" ref="base.module_category_medical_lab"/>
</record>

<record id="group_lab_doctor" model="res.groups">
    <field name="name">Lab Doctor</field>
    <field name="category_id" ref="base.module_category_medical_lab"/>
</record>

<record id="group_lab_manager" model="res.groups">
    <field name="name">Lab Manager</field>
    <field name="category_id" ref="base.module_category_medical_lab"/>
</record>
```

### 5.2 Access Rights Matrix
| Model | Reception | Technician | Doctor | Manager |
|-------|-----------|------------|---------|----------|
| Patient | CRUD | Read | Read | CRUD |
| Invoice | CRUD | Read | Read | CRUD |
| Test Request | CRU | CRUD | CRUD | CRUD |
| Test Config | Read | Read | Read | CRUD |
| Reports | Read | Read | Read | CRUD |

## 6. Integration Points

### 6.1 Odoo Native Integration
- **Accounting**: Invoice generation and payment tracking
- **Inventory**: Sample tracking and consumables
- **Calendar**: Appointment scheduling (future)
- **Website**: Patient portal (future)

### 6.2 External Integration (Future)
- **Lab Machines**: Direct result import via HL7/ASTM protocols
- **SMS Gateway**: Result notifications
- **WhatsApp API**: Report delivery
- **Insurance Systems**: Claim processing

## 7. Performance Requirements

### 7.1 Response Times
- Patient search: < 1 second
- Invoice creation: < 2 seconds
- Report generation: < 5 seconds
- Bulk operations: < 30 seconds for 100 records

### 7.2 Scalability
- Support 10,000+ patients
- Handle 500+ daily invoices
- Store 1M+ test results
- Concurrent users: 50+

## 8. Data Management

### 8.1 Data Retention
- Patient records: Permanent
- Test results: 7 years minimum
- Financial records: As per accounting standards
- Audit logs: 2 years

### 8.2 Backup Requirements
- Daily automated backups
- Point-in-time recovery capability
- Off-site backup storage

## 9. Compliance and Standards

### 9.1 Medical Standards
- HIPAA compliance for data privacy
- HL7 compatibility for data exchange
- ISO 15189 laboratory standards

### 9.2 Financial Standards
- Local tax compliance
- Accounting standards compliance
- Audit trail maintenance

## 10. Implementation Phases

### Phase 1: Core Functionality (MVP)
- Patient management
- Basic invoice creation
- Test configuration
- Sample collection workflow
- Basic reporting

### Phase 2: Enhanced Features
- Advanced test result entry
- Department-wise workflows
- Barcode scanning
- Enhanced reporting

### Phase 3: Integration & Automation
- Machine integration
- Patient portal
- Mobile app
- Advanced analytics

## 11. Module Structure

```
medical_lab_management/
├── __init__.py
├── __manifest__.py
├── security/
│   ├── ir.model.access.csv
│   └── medical_lab_security.xml
├── data/
│   ├── medical_lab_data.xml
│   └── report_paperformat.xml
├── models/
│   ├── __init__.py
│   ├── res_partner.py
│   ├── account_move.py
│   ├── medical_lab_test.py
│   ├── medical_lab_test_request.py
│   ├── medical_lab_category.py
│   ├── medical_lab_department.py
│   └── medical_lab_machine.py
├── views/
│   ├── res_partner_views.xml
│   ├── account_move_views.xml
│   ├── medical_lab_test_views.xml
│   ├── medical_lab_menus.xml
│   └── medical_lab_templates.xml
├── reports/
│   ├── worksheet_report.xml
│   ├── barcode_report.xml
│   ├── receipt_report.xml
│   └── test_result_report.xml
├── wizard/
│   ├── __init__.py
│   └── sample_collection_wizard.py
├── static/
│   ├── src/
│   │   ├── js/
│   │   └── scss/
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    └── test_medical_lab.py
```

## 12. Success Metrics

### 12.1 Operational Metrics
- Patient processing time reduction: 50%
- Error rate in test results: < 0.1%
- Report generation time: < 5 minutes
- Sample tracking accuracy: 99.9%

### 12.2 Financial Metrics
- Invoice accuracy: 99.9%
- Payment collection efficiency: 95%
- Cost reduction: 30%

### 12.3 User Satisfaction
- User adoption rate: > 90%
- Training time: < 2 hours
- Support tickets: < 5 per month

## 13. Risk Management

### 13.1 Technical Risks
- Data migration complexity
- Integration challenges
- Performance bottlenecks
- Security vulnerabilities

### 13.2 Mitigation Strategies
- Phased implementation
- Comprehensive testing
- Regular security audits
- Performance monitoring
- User training programs

## 14. Maintenance and Support

### 14.1 Regular Updates
- Bug fixes: Monthly
- Security patches: As needed
- Feature updates: Quarterly
- Major versions: Annually

### 14.2 Support Levels
- Level 1: User assistance
- Level 2: Technical support
- Level 3: Developer support
- Emergency: 24/7 availability

## 15. Future Enhancements

### 15.1 Short Term (6 months)
- Mobile application
- Advanced analytics dashboard
- Automated result validation
- Multi-language support

### 15.2 Long Term (1-2 years)
- AI-powered diagnosis assistance
- Blockchain for result verification
- IoT device integration
- Telemedicine integration

## Appendices

### A. Glossary
- **MLMS**: Medical Lab Management System
- **LIS**: Laboratory Information System
- **HL7**: Health Level Seven International
- **ASTM**: American Society for Testing and Materials
- **HIPAA**: Health Insurance Portability and Accountability Act

### B. References
- Odoo Development Documentation
- ISO 15189:2012 Medical laboratories standards
- HL7 Implementation Guide
- Local healthcare regulations

### C. Change Log
- Version 1.0.0: Initial PRD creation
- Last Updated: 2024-12-26
- Author: Medical Lab Management Team