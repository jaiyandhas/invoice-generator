const express = require('express');
const router = express.Router();
const db = require('../database');

// Get all customers
router.get('/', (req, res) => {
  db.all('SELECT * FROM customers', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Create new customer
router.post('/', (req, res) => {
  const { name, email, phone, address } = req.body;
  db.run(
    'INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)',
    [name, email, phone, address],
    function(err) {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json({ id: this.lastID });
    }
  );
});

module.exports = router;