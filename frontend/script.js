document.addEventListener('DOMContentLoaded', function() {
    // Tab navigation
    const navButtons = document.querySelectorAll('.nav-btn');
    const contentSections = document.querySelectorAll('.content-section');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active button
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Show corresponding section
            const target = button.getAttribute('data-target');
            contentSections.forEach(section => {
                section.classList.remove('active');
                if (section.id === target) {
                    section.classList.add('active');
                    
                    // Load data when section becomes active
                    if (target === 'customer-section') loadCustomers();
                    if (target === 'invoice-section') loadInvoices();
                    if (target === 'create-invoice') loadCustomerDropdown();
                }
            });
        });
    });
    
    // Customer management
    document.getElementById('add-customer').addEventListener('click', addCustomer);
    
    // Invoice management
    document.getElementById('add-item').addEventListener('click', addItemRow);
    document.getElementById('save-invoice').addEventListener('click', saveInvoice);
    
    // Initialize the first tab
    document.querySelector('.nav-btn.active').click();
    
    // Event delegation for dynamic elements
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item')) {
            e.target.closest('.item-row').remove();
            calculateInvoiceTotal();
        }
    });
});

// Customer functions
function loadCustomers() {
    fetch('/api/customers')
        .then(response => response.json())
        .then(customers => {
            const tbody = document.querySelector('#customer-table tbody');
            tbody.innerHTML = '';
            
            customers.forEach(customer => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${customer.id}</td>
                    <td>${customer.name}</td>
                    <td>${customer.email || '-'}</td>
                    <td>
                        <button class="edit-btn" data-id="${customer.id}">Edit</button>
                        <button class="delete-btn" data-id="${customer.id}">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

function addCustomer() {
    const name = document.getElementById('customer-name').value;
    const email = document.getElementById('customer-email').value;
    
    if (!name) {
        alert('Customer name is required');
        return;
    }
    
    fetch('/api/customers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email })
    })
    .then(response => response.json())
    .then(() => {
        loadCustomers();
        document.getElementById('customer-name').value = '';
        document.getElementById('customer-email').value = '';
    });
}

// Invoice functions
function loadInvoices() {
    fetch('/api/invoices')
        .then(response => response.json())
        .then(invoices => {
            const tbody = document.querySelector('#invoice-table tbody');
            tbody.innerHTML = '';
            
            invoices.forEach(invoice => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${invoice.invoice_number}</td>
                    <td>${invoice.customer_name || 'No customer'}</td>
                    <td>${invoice.date}</td>
                    <td>$${invoice.total.toFixed(2)}</td>
                    <td>${invoice.status}</td>
                    <td>
                        <button class="view-btn" data-id="${invoice.id}">View</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

function loadCustomerDropdown() {
    fetch('/api/customers')
        .then(response => response.json())
        .then(customers => {
            const select = document.getElementById('select-customer');
            select.innerHTML = '<option value="">Select Customer</option>';
            
            customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = customer.name;
                select.appendChild(option);
            });
        });
}

function addItemRow() {
    const itemsContainer = document.getElementById('invoice-items');
    const newRow = document.createElement('div');
    newRow.className = 'item-row';
    newRow.innerHTML = `
        <input type="text" class="item-desc" placeholder="Description">
        <input type="number" class="item-qty" placeholder="Qty" min="1" value="1">
        <input type="number" class="item-price" placeholder="Price" min="0" step="0.01" value="0">
        <span class="item-total">0.00</span>
        <button class="remove-item">×</button>
    `;
    itemsContainer.appendChild(newRow);
    
    // Add event listeners for calculations
    const qtyInput = newRow.querySelector('.item-qty');
    const priceInput = newRow.querySelector('.item-price');
    const totalSpan = newRow.querySelector('.item-total');
    
    function calculateItemTotal() {
        const qty = parseFloat(qtyInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = qty * price;
        totalSpan.textContent = total.toFixed(2);
        calculateInvoiceTotal();
    }
    
    qtyInput.addEventListener('input', calculateItemTotal);
    priceInput.addEventListener('input', calculateItemTotal);
    
    // Initial calculation
    calculateItemTotal();
}

function calculateInvoiceTotal() {
    let total = 0;
    document.querySelectorAll('.item-row').forEach(row => {
        const itemTotal = parseFloat(row.querySelector('.item-total').textContent) || 0;
        total += itemTotal;
    });
    document.getElementById('invoice-total').textContent = total.toFixed(2);
}

function saveInvoice() {
    const customerId = document.getElementById('select-customer').value;
    const date = document.getElementById('invoice-date').value;
    
    if (!customerId || !date) {
        alert('Please select a customer and enter a date');
        return;
    }
    
    const items = [];
    document.querySelectorAll('.item-row').forEach(row => {
        const description = row.querySelector('.item-desc').value;
        const quantity = parseFloat(row.querySelector('.item-qty').value);
        const unitPrice = parseFloat(row.querySelector('.item-price').value);
        
        if (description && quantity && unitPrice) {
            items.push({
                description,
                quantity,
                unit_price: unitPrice,
                total: quantity * unitPrice
            });
        }
    });
    
    if (items.length === 0) {
        alert('Please add at least one item');
        return;
    }
    
    fetch('/api/invoices', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            customer_id: customerId,
            date: date,
            items: items
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(`Invoice ${data.invoice_number} created successfully!`);
        document.querySelector('[data-target="invoice-section"]').click();
    });
}