# Medical Lab Management System for Odoo

A comprehensive laboratory management module for Odoo that streamlines the entire lab workflow from patient registration to test result delivery.

## Features

### Core Functionality
- **Patient Management**: Extends `res.partner` to manage patient records
- **Doctor/Referral Management**: Track referring doctors and their referrals
- **Invoice Integration**: Leverages Odoo's invoicing system for billing
- **Sample Tracking**: Barcode-based sample identification and tracking
- **Test Configuration**: Flexible test setup with multiple result types
- **Workflow Management**: Complete workflow from registration to result delivery
- **Multi-department Support**: Organize tests by departments and machines
- **Report Generation**: Multiple report formats including worksheets, receipts, and results

### Workflow Steps
1. **Patient Registration** - Create or find existing patients
2. **Invoice Creation** - Generate invoices with selected tests
3. **Sample Collection** - Print barcodes and worksheets
4. **Diagnosis** - Record test results
5. **Printing** - Generate result reports
6. **Signature & Delivery** - Final verification and delivery

## Installation

1. **Prerequisites**
   ```bash
   # Required Python packages
   pip install python-barcode[images]
   pip install python-dateutil
   ```

2. **Module Installation**
   - Copy the `medical_lab_management` folder to your Odoo addons directory
   - Update the addons list in Odoo
   - Install the module from Apps menu

## Configuration

### Initial Setup

1. **User Groups**: The module creates the following security groups:
   - Lab Reception
   - Lab Technician
   - Lab Doctor
   - Lab Manager

2. **Basic Data**:
   - Create departments (Hematology, Chemistry, etc.)
   - Add lab machines if needed
   - Configure common tests
   - Set up price lists

### Test Configuration

Tests support four result types:

1. **Selection Type**: Fixed options (e.g., Positive/Negative)
   ```json
   [
     {"value": "positive", "label": "Positive"},
     {"value": "negative", "label": "Negative"}
   ]
   ```

2. **Range Type**: Numeric values with normal ranges
   - Universal ranges for all patients
   - Demographic-specific ranges (by age/gender)

3. **Quantitative Type**: Simple numeric values

4. **Descriptive Type**: Free-text results

## Usage

### Patient Registration

1. Navigate to **Medical Lab → Patients**
2. Search for existing patient or create new
3. Patient ID is auto-generated (format: PAT/2024/00001)
4. Age is automatically calculated from date of birth

### Creating Lab Invoice

1. From patient record, click **Create Invoice** or navigate to **Medical Lab → Invoices**
2. Select patient and referring doctor
3. Add required tests
4. Enter payment details
5. Confirm invoice to generate barcode

### Sample Collection

1. Print worksheet (contains all test details)
2. Print barcode sticker
3. Update status to "Sample Collected"
4. Distribute to appropriate departments

### Recording Results

1. Navigate to **Medical Lab → Laboratory → Diagnosis**
2. Select test request
3. Enter results based on test type
4. Mark as completed

### Generating Reports

The module includes several report templates:
- **Worksheet**: For sample collection and manual result entry
- **Barcode Sticker**: For sample identification
- **Receipt**: Payment receipt for patients
- **Test Results**: Final report with all test results

## Module Structure

```
medical_lab_management/
├── models/
│   ├── res_partner.py          # Patient & Doctor management
│   ├── account_move.py         # Lab invoice extensions
│   ├── medical_lab_test.py     # Test configuration
│   └── medical_lab_test_request.py  # Test requests/results
├── views/
│   ├── res_partner_views.xml   # Patient & Doctor views
│   ├── account_move_views.xml  # Invoice views
│   └── medical_lab_test_views.xml  # Test configuration views
├── security/
│   ├── ir.model.access.csv     # Access rights
│   └── medical_lab_security.xml # Security groups
├── reports/
│   └── *.xml                   # Report templates
└── data/
    └── medical_lab_sequence.xml # ID sequences
```

## API Reference

### Key Models

#### res.partner (Extended)
- `is_patient`: Boolean flag for patients
- `patient_id`: Unique patient identifier
- `is_doctor`: Boolean flag for doctors
- `doctor_id`: Unique doctor identifier

#### account.move (Extended)
- `is_lab_invoice`: Boolean flag for lab invoices
- `patient_id`: Link to patient
- `barcode_id`: Unique barcode for sample
- `sample_status`: Workflow status
- `lab_test_ids`: Test requests

#### medical.lab.test
- Main test configuration model
- Supports multiple result types
- Price list management
- Normal range configuration

## Customization

### Adding New Test Types

1. Create test record with appropriate result type
2. Configure normal ranges if applicable
3. Set up pricing
4. Assign to department/category

### Custom Reports

Reports can be customized by:
1. Modifying XML report templates
2. Creating custom QWeb templates
3. Adding company-specific headers/footers

## Troubleshooting

### Common Issues

1. **Barcode Generation Fails**
   - Ensure `python-barcode` package is installed
   - Check sequence configuration

2. **Age Calculation Error**
   - Verify `python-dateutil` is installed
   - Check date format settings

3. **Access Rights Issues**
   - Verify user is assigned to appropriate group
   - Check ir.model.access.csv entries

## Future Enhancements

- Machine integration for automated result import
- Patient portal for online result access
- SMS/Email notifications
- Advanced analytics dashboard
- Mobile application support

## Support

For issues, feature requests, or contributions, please contact the development team or raise an issue in the project repository.

## License

This module is licensed under LGPL-3.0. See LICENSE file for details.