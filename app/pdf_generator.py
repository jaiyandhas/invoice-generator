from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
from typing import Union, Optional

def generate_pdf(invoice, output_path: Optional[str] = None) -> Union[BytesIO, str]:
    """
    Generate a PDF invoice from an invoice object.
    
    Args:
        invoice: The invoice object containing all necessary data
        output_path: Optional path to save the PDF directly to a file
        
    Returns:
        BytesIO buffer if no output_path provided, otherwise returns the file path
    """
    try:
        # Initialize buffer or file path
        buffer = BytesIO() if output_path is None else None
        
        # Create document with margins
        doc = SimpleDocTemplate(
            buffer if buffer else output_path,
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        styles = getSampleStyleSheet()
        
        # Add custom styles
        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            alignment=2  # 0=left, 1=center, 2=right
        ))
        
        elements = []
        
        # Header section
        header_table = Table([
            [
                Paragraph("INVOICE", styles['Title']),
                Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}<br/>"
                         f"<b>Date:</b> {invoice.issue_date.strftime('%B %d, %Y')}<br/>"
                         f"<b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y')}",
                         styles['Normal'])
            ]
        ], colWidths=[4*inch, 2*inch])
        
        elements.append(header_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Customer Info
        customer_info = [
            Paragraph("<b>Bill To:</b>", styles['Heading3']),
            Paragraph(invoice.customer.name, styles['Normal'])
        ]
        
        if invoice.customer.address:
            address_lines = invoice.customer.address.split('\n')
            for line in address_lines:
                customer_info.append(Paragraph(line, styles['Normal']))
        
        if invoice.customer.email:
            customer_info.append(Paragraph(invoice.customer.email, styles['Normal']))
        
        if invoice.customer.phone:
            customer_info.append(Paragraph(invoice.customer.phone, styles['Normal']))
        
        elements.extend(customer_info)
        elements.append(Spacer(1, 0.5*inch))
        
        # Line Items Table
        data = [
            [
                Paragraph('<b>Description</b>', styles['Normal']),
                Paragraph('<b>Qty</b>', styles['Normal']),
                Paragraph('<b>Unit Price</b>', styles['Normal']),
                Paragraph('<b>Amount</b>', styles['Normal'])
            ]
        ]
        
        for item in invoice.items:
            data.append([
                Paragraph(item.description, styles['Normal']),
                Paragraph(str(item.quantity), styles['RightAlign']),
                Paragraph(f"${item.unit_price:,.2f}", styles['RightAlign']),
                Paragraph(f"${item.amount:,.2f}", styles['RightAlign'])
            ])
        
        # Configure table
        table = Table(
            data,
            colWidths=[3.5*inch, 0.75*inch, inch, inch],
            hAlign='LEFT'
        )
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#404040')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F5F5F5')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Totals Section
        totals_data = [
            ['', '', Paragraph('<b>Subtotal:</b>', styles['RightAlign']), 
             Paragraph(f"${invoice.subtotal:,.2f}", styles['RightAlign'])],
        ]
        
        if invoice.tax_rate > 0:
            totals_data.append([
                '', '', Paragraph(f'<b>Tax ({invoice.tax_rate}%):</b>', styles['RightAlign']),
                Paragraph(f"${invoice.tax_amount:,.2f}", styles['RightAlign'])
            ])
        
        totals_data.append([
            '', '', Paragraph('<b>Total:</b>', styles['Heading3']),
            Paragraph(f"${invoice.total:,.2f}", styles['Heading3'])
        ])
        
        totals_table = Table(
            totals_data,
            colWidths=[3.5*inch, 0.75*inch, inch, inch]
        )
        
        elements.append(totals_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Terms and Notes
        if invoice.notes:
            elements.append(Paragraph("<b>Notes:</b>", styles['Heading3']))
            elements.append(Paragraph(invoice.notes, styles['Normal']))
            elements.append(Spacer(1, 0.25*inch))
        
        if invoice.terms:
            elements.append(Paragraph("<b>Terms:</b>", styles['Heading3']))
            elements.append(Paragraph(invoice.terms, styles['Normal']))
        
        # Build the document
        doc.build(elements)
        
        if buffer:
            buffer.seek(0)
            return buffer
        return output_path
        
    except Exception as e:
        # Log the error in production
        raise RuntimeError(f"Failed to generate PDF: {str(e)}")