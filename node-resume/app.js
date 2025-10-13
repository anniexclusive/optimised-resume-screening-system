const express = require('express')
const app = express()
const path = require('path');
const cors = require("cors");
const config = require('./config/api.config');

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

// Middleware
app.use(cors({
  origin: config.cors.origin,
  credentials: config.cors.credentials
}));
app.use(express.json());

const resume = require('./resume');

// API route
app.get('/api', (req, res) => {
  res.json({ message: 'Hello World from Node.js backend!' });
});
// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.use(resume);

app.listen(config.server.port, () => {
  console.log(`Server is running on http://${config.server.host}:${config.server.port}`);
  console.log(`Environment: ${config.env}`);
});