from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateField,
    SelectField,
    DecimalField,
    TextAreaField,
    SubmitField,
    FieldList,
    FormField,
    HiddenField
)
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from datetime import date

class CustomerForm(FlaskForm):
    """Form for adding/editing customers"""
    name = StringField('Full Name', validators=[DataRequired()],
                     render_kw={"class": "form-control"})
    email = StringField('Email', validators=[Optional(), Email()],
                      render_kw={"class": "form-control", "type": "email"})
    phone = StringField('Phone', validators=[Optional()],
                      render_kw={"class": "form-control", "type": "tel"})
    address = TextAreaField('Address', validators=[Optional()],
                          render_kw={"class": "form-control", "rows": 3})
    submit = SubmitField('Save Customer',
                       render_kw={"class": "btn btn-primary"})

class InvoiceItemForm(FlaskForm):
    """Subform for individual invoice items"""
    description = StringField('Description', validators=[DataRequired()],
                            render_kw={"class": "form-control"})
    quantity = DecimalField(
        'Qty',
        validators=[DataRequired(), NumberRange(min=0.01)],
        render_kw={
            "class": "form-control",
            "step": "0.01",
            "min": "0.01",
            "type": "number"
        }
    )
    unit_price = DecimalField(
        'Unit Price',
        validators=[DataRequired(), NumberRange(min=0.01)],
        render_kw={
            "class": "form-control",
            "step": "0.01",
            "min": "0.01",
            "type": "number"
        }
    )

class InvoiceForm(FlaskForm):
    """Main invoice form"""
    customer_id = SelectField(
        'Customer',
        coerce=int,
        validators=[DataRequired(message="Please select a customer")],
        render_kw={
            "class": "form-select",
            "aria-label": "Customer selection"
        }
    )
    issue_date = DateField(
        'Issue Date',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "type": "date"
        }
    )
    due_date = DateField(
        'Due Date',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "type": "date"
        }
    )
    tax_rate = DecimalField(
        'Tax Rate (%)',
        validators=[Optional(), NumberRange(min=0, max=100)],
        default=0.0,
        render_kw={
            "class": "form-control",
            "step": "0.01",
            "type": "number",
            "min": "0",
            "max": "100"
        }
    )
    notes = TextAreaField('Notes', validators=[Optional()],
                        render_kw={"class": "form-control", "rows": 3})
    subtotal = DecimalField(
        'Subtotal',
        render_kw={
            "class": "form-control",
            "readonly": True,
            "step": "0.01",
            "type": "number"
        }
    )
    tax_amount = DecimalField(
        'Tax Amount',
        render_kw={
            "class": "form-control",
            "readonly": True,
            "step": "0.01",
            "type": "number"
        }
    )
    total = DecimalField(
        'Total',
        render_kw={
            "class": "form-control",
            "readonly": True,
            "step": "0.01",
            "type": "number"
        }
    )
    submit = SubmitField('Save Invoice',
                       render_kw={"class": "btn btn-primary"})