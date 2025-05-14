# 🧾 Simple Invoice Generator

A lightweight web-based Invoice Generator built using Python and Flask. This project was developed as a DBMS Mini Project to demonstrate real-world application of database modeling, form handling, and PDF generation.

---

## 📌 Project Objectives

- Manage customer and invoice data efficiently using a relational database
- Dynamically generate professional invoices
- Provide a simple, clean, and interactive user interface
- Allow PDF download and printing of invoices
- Apply real-world CRUD operations using Flask and SQLAlchemy

---

## 🛠️ Technologies Used

| Layer        | Tool/Library             | Purpose                                 |
|-------------|---------------------------|-----------------------------------------|
| Backend     | Python, Flask             | Server-side logic and routing           |
| Frontend    | HTML, CSS, Bootstrap      | User interface and layout               |
| Forms       | Flask-WTF, WTForms        | Form validation and input handling      |
| Database    | SQLAlchemy (ORM)          | Object-relational database modeling     |
| PDF Engine  | ReportLab                 | PDF invoice generation                  |
| Templates   | Jinja2                    | Dynamic HTML rendering                  |

---

## 🗃️ Database Design

- **Customer Table**: Stores customer info
- **Invoice Table**: Stores invoice metadata (linked to customer)
- **InvoiceItem Table**: Stores items in each invoice (linked to invoice)

### 🔗 Relationships

- One Customer → Many Invoices  
- One Invoice → Many Invoice Items

---

## 🚀 Features

- Create, read, update, and delete customers and invoices
- Add multiple items per invoice with quantity, rate, and tax
- Automatically calculate subtotal, tax, and total
- Download professional PDF invoices
- Dashboard with invoice status tracking

---

## 📂 Project Structure

