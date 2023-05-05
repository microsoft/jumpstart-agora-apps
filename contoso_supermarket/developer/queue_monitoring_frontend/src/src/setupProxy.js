const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
    app.use(createProxyMiddleware("/api", { target: process.env.BACKEND_API_URL, secure: false }));
    app.use(
        createProxyMiddleware("/ai", {
            target: process.env.AI_API_URL,
            secure: false,
            pathRewrite: {
                "^/ai": "", //remove /ai from the path
            },
        })
    );
};
