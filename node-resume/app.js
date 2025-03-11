const express = require('express')
const app = express()
const path = require('path');
const PORT = 5000;
const cors = require("cors");
// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));
// Middleware
app.use(cors());
app.use(express.json());

const resume = require('./resume');

// API route
app.get('/api', (req, res) => {
  res.json({ message: 'Hello World from Node.js backend!' });
});
app.use(resume);

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});