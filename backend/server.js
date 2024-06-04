const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = 8080;

// Middleware to parse JSON bodies
app.use(express.json());

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
