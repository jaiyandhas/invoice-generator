const express = require('express');
const router = express.Router();
const db = require('../database');

// Get all invoices with customer names
router.get('/', (req, res) => {
  const sql = `
    SELECT i.*, c.name as customer_name 
    FROM invoices i
    LEFT JOIN customers c ON i.customer_id = c.id
  `;
  db.all(sql, [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Create new invoice with items
router.post('/', (req, res) => {
  const { customer_id, date, due_date, items } = req.body;
  const invoice_number = 'INV-' + Date.now();
  const total = items.reduce((sum, item) => sum + item.total, 0);

  db.serialize(() => {
    db.run(
      'INSERT INTO invoices (customer_id, invoice_number, date, due_date, total) VALUES (?, ?, ?, ?, ?)',
      [customer_id, invoice_number, date, due_date, total],
      function(err) {
        if (err) {
          res.status(500).json({ error: err.message });
          return;
        }
        const invoiceId = this.lastID;

        // Insert invoice items
        const stmt = db.prepare(
          'INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total) VALUES (?, ?, ?, ?, ?)'
        );
        
        items.forEach(item => {
          stmt.run([invoiceId, item.description, item.quantity, item.unit_price, item.total]);
        });
        
        stmt.finalize();
        res.json({ id: invoiceId, invoice_number });
      }
    );
  });
});

module.exports = router;