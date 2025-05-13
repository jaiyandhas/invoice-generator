from datetime import datetime
from app import db
from app.models import Invoice, Customer
import os

def generate_invoice_number():
    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    return f"INV-{(last_invoice.id + 1) if last_invoice else 1:04d}"

def calculate_totals(items, tax_rate):
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    return {
        'subtotal': round(subtotal, 2),
        'tax_amount': round(tax_amount, 2),
        'total': round(subtotal + tax_amount, 2)
    }

def save_pdf_to_disk(invoice):
    os.makedirs('app/static/invoices', exist_ok=True)
    pdf_path = f'app/static/invoices/invoice_{invoice.invoice_number}.pdf'
    from app.pdf_generator import generate_pdf
    generate_pdf(invoice, pdf_path)
    return pdf_path