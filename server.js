const express = require('express');
const bodyParser = require('body-parser');
const db = require('./database');
const path = require('path');

const app = express();

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'frontend')));

// API Routes
app.use('/api/customers', require('./models/customer'));
app.use('/api/invoices', require('./models/invoice'));

// Serve frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});