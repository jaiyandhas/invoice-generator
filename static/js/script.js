document.addEventListener('DOMContentLoaded', function() {
    // Add item row to invoice form
    document.getElementById('add-item')?.addEventListener('click', function() {
        const itemsTable = document.querySelector('#items-table tbody');
        const newRow = itemsTable.insertRow();
        
        newRow.innerHTML = `
            <td><input type="text" name="description" class="form-control" required></td>
            <td><input type="number" name="quantity" class="form-control calc-total" min="0" step="0.01" required></td>
            <td><input type="number" name="unit_price" class="form-control calc-total" min="0" step="0.01" required></td>
            <td><input type="number" name="amount" class="form-control" readonly></td>
            <td><button type="button" class="btn btn-danger remove-row">×</button></td>
        `;
        
        // Add event listeners to new row
        newRow.querySelectorAll('.calc-total').forEach(input => {
            input.addEventListener('input', calculateRowTotal);
        });
        newRow.querySelector('.remove-row').addEventListener('click', removeRow);
    });

    // Calculate row total
    function calculateRowTotal(e) {
        const row = e.target.closest('tr');
        const quantity = parseFloat(row.querySelector('[name="quantity"]').value) || 0;
        const unitPrice = parseFloat(row.querySelector('[name="unit_price"]').value) || 0;
        const amount = quantity * unitPrice;
        row.querySelector('[name="amount"]').value = amount.toFixed(2);
        calculateInvoiceTotals();
    }

    // Remove row
    function removeRow(e) {
        e.target.closest('tr').remove();
        calculateInvoiceTotals();
    }

    // Calculate all invoice totals
    function calculateInvoiceTotals() {
        let subtotal = 0;
        document.querySelectorAll('[name="amount"]').forEach(input => {
            subtotal += parseFloat(input.value) || 0;
        });

        const taxRate = parseFloat(document.getElementById('tax_rate').value) || 0;
        const taxAmount = subtotal * (taxRate / 100);
        const total = subtotal + taxAmount;

        document.getElementById('subtotal').value = subtotal.toFixed(2);
        document.getElementById('tax_amount').value = taxAmount.toFixed(2);
        document.getElementById('total').value = total.toFixed(2);
    }

    // Initialize calculations for existing rows
    document.querySelectorAll('.calc-total').forEach(input => {
        input.addEventListener('input', calculateRowTotal);
    });
    document.querySelectorAll('.remove-row').forEach(btn => {
        btn.addEventListener('click', removeRow);
    });
    document.getElementById('tax_rate')?.addEventListener('input', calculateInvoiceTotals);
});