const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(createProxyMiddleware('/api', { target: process.env.BACKEND_API_URL, secure: false  }));
};