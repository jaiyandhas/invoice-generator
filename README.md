# Invoice Generator System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A web-based invoice generation system built with Flask that allows users to:
- Create and manage customer records
- Generate professional invoices with line items
- Automatically calculate taxes and totals
- Export invoices as PDF documents
- Track invoice status (Draft/Paid/Overdue)

## Features

- **Customer Management**: Add, edit, and view customer information
- **Invoice Creation**: 
  - Dynamic line items with quantity/price calculations
  - Automatic tax calculations
  - Customizable invoice numbering
- **PDF Generation**: Professional invoice templates
- **Dashboard**: View all invoices with status indicators
- **Search & Filter**: Find invoices by customer, date, or status

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (can be configured for MySQL/PostgreSQL)
- **PDF Generation**: ReportLab
- **Frontend**: Bootstrap 5, Jinja2 templates
- **ORM**: SQLAlchemy

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jaiyandhas/invoice-generator.git
   cd invoice-generator
