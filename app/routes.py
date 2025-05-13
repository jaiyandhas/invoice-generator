from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from app import db
from app.models import Customer, Invoice, InvoiceItem
from app.forms import CustomerForm, InvoiceForm
from app.utils import generate_invoice_number, calculate_totals
from app.pdf_generator import generate_pdf
from datetime import datetime, timedelta
import os
import logging
from io import BytesIO
from sqlalchemy.orm import joinedload

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprints
main_routes = Blueprint('main', __name__)
customer_routes = Blueprint('customers', __name__, url_prefix='/customers')
invoice_routes = Blueprint('invoices', __name__, url_prefix='/invoices')

# PDF Configuration
PDF_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'pdfs')
os.makedirs(PDF_DIR, exist_ok=True)

def get_customer_choices():
    """Get customer choices for dropdown with formatted display"""
    try:
        customers = Customer.query.order_by(Customer.name).all()
        return [(c.id, f"{c.name} ({c.email})" if c.email else c.name) for c in customers]
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        flash('Error loading customer list', 'danger')
        return []

# Main Routes
@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/dashboard')
def dashboard():
    try:
        total_customers = Customer.query.count()
        total_invoices = Invoice.query.count()
        recent_invoices = Invoice.query.order_by(Invoice.issue_date.desc()).limit(5).all()
        return render_template('dashboard.html', 
                            total_customers=total_customers,
                            total_invoices=total_invoices, 
                            recent_invoices=recent_invoices)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('main.index'))

# Customer Routes
@customer_routes.route('/', methods=['GET', 'POST'])
def list_customers():
    form = CustomerForm()
    if form.validate_on_submit():
        try:
            customer = Customer(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data
            )
            db.session.add(customer)
            db.session.commit()
            flash('Customer created successfully!', 'success')
            return redirect(url_for('customers.list_customers'))
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            flash('Error creating customer', 'danger')

    customers = Customer.query.order_by(Customer.name).all()
    return render_template('customers/list.html', customers=customers, form=form)

@customer_routes.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(customer)
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers.list_customers'))
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            flash('Error updating customer', 'danger')

    return render_template('customers/edit.html', customer=customer, form=form)

@customer_routes.route('/<int:id>/delete', methods=['POST'])
def delete_customer(id):
    try:
        customer = Customer.query.get_or_404(id)
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        flash('Error deleting customer', 'danger')
    return redirect(url_for('customers.list_customers'))

# Invoice Routes
@invoice_routes.route('/')
def list_invoices():
    try:
        invoices = Invoice.query.options(
            joinedload(Invoice.customer)
        ).order_by(Invoice.issue_date.desc()).all()
        return render_template('invoices/list.html', invoices=invoices)
    except Exception as e:
        logger.error(f"Error listing invoices: {str(e)}")
        flash('Error loading invoices', 'danger')
        return redirect(url_for('main.index'))

@invoice_routes.route('/create', methods=['GET', 'POST'])
def create_invoice():
    form = InvoiceForm()
    form.customer_id.choices = [(0, "-- Select Customer --")] + get_customer_choices()
    
    if request.method == 'GET':
        form.issue_date.data = datetime.today()
        form.due_date.data = datetime.today() + timedelta(days=30)
    
    if form.validate_on_submit():
        try:
            if form.customer_id.data == 0:
                flash('Please select a customer', 'danger')
                return render_template('invoices/create.html', form=form)
            
            descriptions = request.form.getlist('description')
            quantities = request.form.getlist('quantity')
            prices = request.form.getlist('unit_price')

            items = []
            for desc, qty, price in zip(descriptions, quantities, prices):
                if desc:
                    items.append({
                        'description': desc,
                        'quantity': float(qty),
                        'unit_price': float(price)
                    })

            if not items:
                flash('At least one invoice item is required', 'danger')
                return render_template('invoices/create.html', form=form)

            totals = calculate_totals(items, float(form.tax_rate.data))

            invoice = Invoice(
                invoice_number=generate_invoice_number(),
                customer_id=form.customer_id.data,
                issue_date=form.issue_date.data,
                due_date=form.due_date.data,
                subtotal=totals['subtotal'],
                tax_rate=form.tax_rate.data,
                tax_amount=totals['tax_amount'],
                total=totals['total'],
                notes=form.notes.data,
                status='DRAFT'
            )
            
            db.session.add(invoice)
            db.session.commit()

            for item in items:
                db.session.add(InvoiceItem(
                    invoice_id=invoice.id,
                    description=item['description'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    amount=item['quantity'] * item['unit_price']
                ))

            db.session.commit()
            flash('Invoice created successfully!', 'success')
            return redirect(url_for('invoices.view_invoice', id=invoice.id))
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            flash('Error creating invoice', 'danger')
            db.session.rollback()

    return render_template('invoices/create.html', form=form)

@invoice_routes.route('/<int:id>')
def view_invoice(id):
    try:
        invoice = db.session.query(Invoice).\
            options(
                joinedload(Invoice.customer),
                joinedload(Invoice.items)
            ).\
            filter(Invoice.id == id).\
            one()
        
        logger.info(f"Invoice loaded - ID: {invoice.id}, Customer: {invoice.customer.name if invoice.customer else 'None'}, Items: {len(invoice.items)}")
        
        # Add debug output
        print(f"Invoice Status: {invoice.status}")  # Check status case sensitivity
        print(f"Customer Exists: {invoice.customer is not None}")
        print(f"Items Count: {len(invoice.items)}")
        
        return render_template('invoices/view.html', invoice=invoice)
    
    except Exception as e:
        logger.error(f"Error viewing invoice {id}: {str(e)}", exc_info=True)
        flash('Error loading invoice', 'danger')
        return redirect(url_for('invoices.list_invoices'))

@invoice_routes.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_invoice(id):
    invoice = Invoice.query.options(
        joinedload(Invoice.customer),
        joinedload(Invoice.items)
    ).get_or_404(id)
    
    form = InvoiceForm(obj=invoice)
    form.customer_id.choices = get_customer_choices()
    
    if form.validate_on_submit():
        try:
            form.populate_obj(invoice)
            InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()

            descriptions = request.form.getlist('description')
            quantities = request.form.getlist('quantity')
            prices = request.form.getlist('unit_price')

            items = []
            for desc, qty, price in zip(descriptions, quantities, prices):
                if desc:
                    items.append({
                        'description': desc,
                        'quantity': float(qty),
                        'unit_price': float(price)
                    })

            if not items:
                flash('At least one invoice item is required', 'danger')
                return render_template('invoices/edit.html', form=form, invoice=invoice)

            totals = calculate_totals(items, float(form.tax_rate.data))
            invoice.subtotal = totals['subtotal']
            invoice.tax_amount = totals['tax_amount']
            invoice.total = totals['total']

            for item in items:
                db.session.add(InvoiceItem(
                    invoice_id=invoice.id,
                    description=item['description'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    amount=item['quantity'] * item['unit_price']
                ))

            db.session.commit()
            flash('Invoice updated successfully!', 'success')
            return redirect(url_for('invoices.view_invoice', id=invoice.id))
            
        except Exception as e:
            logger.error(f"Error updating invoice: {str(e)}")
            flash('Error updating invoice', 'danger')
            db.session.rollback()

    return render_template('invoices/edit.html', form=form, invoice=invoice)

@invoice_routes.route('/<int:id>/delete', methods=['POST'])
def delete_invoice(id):
    try:
        invoice = Invoice.query.get_or_404(id)
        db.session.delete(invoice)
        db.session.commit()
        flash('Invoice deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting invoice: {str(e)}")
        flash('Error deleting invoice', 'danger')
    return redirect(url_for('invoices.list_invoices'))

@invoice_routes.route('/<int:id>/mark-paid', methods=['POST'])
def mark_as_paid(id):
    try:
        invoice = Invoice.query.get_or_404(id)
        invoice.status = 'PAID'
        invoice.payment_date = datetime.today()
        db.session.commit()
        flash('Invoice marked as paid!', 'success')
    except Exception as e:
        logger.error(f"Error marking invoice as paid: {str(e)}")
        flash('Error updating invoice status', 'danger')
    return redirect(url_for('invoices.view_invoice', id=id))

@invoice_routes.route('/<int:id>/pdf')
def download_pdf(id):
    try:
        invoice = Invoice.query.options(
            joinedload(Invoice.customer),
            joinedload(Invoice.items)
        ).get_or_404(id)
        
        pdf_buffer = generate_pdf(invoice)
        
        # Save to disk for future reference
        pdf_filename = f"invoice_{invoice.invoice_number}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getbuffer())
        
        # Return for download
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
        flash('Error generating PDF. Please try again.', 'danger')
        return redirect(url_for('invoices.view_invoice', id=id))

@invoice_routes.route('/<int:id>/print')
def print_invoice(id):
    try:
        invoice = Invoice.query.options(
            joinedload(Invoice.customer),
            joinedload(Invoice.items)
        ).get_or_404(id)
        return render_template('invoices/print.html', invoice=invoice)
    except Exception as e:
        logger.error(f"Error loading invoice for printing: {str(e)}")
        flash('Error loading invoice', 'danger')
        return redirect(url_for('invoices.view_invoice', id=id))

# Debug route
@invoice_routes.route('/<int:id>/debug')
def debug_invoice(id):
    try:
        invoice = Invoice.query.options(
            joinedload(Invoice.customer),
            joinedload(Invoice.items)
        ).get_or_404(id)
        
        return {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'customer': {
                'id': invoice.customer.id,
                'name': invoice.customer.name
            } if invoice.customer else None,
            'items_count': len(invoice.items),
            'status': invoice.status,
            'total': float(invoice.total)
        }
    except Exception as e:
        return {'error': str(e)}, 500