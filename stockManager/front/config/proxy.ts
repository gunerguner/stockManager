export default {
  dev: {
    '/api/': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      pathRewrite: { '^': '' },
    },
  },
  test: {
    '/api/': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      pathRewrite: { '^': '' },
    },
  },
  pre: {
    '/api/': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      pathRewrite: { '^': '' },
    },
  },
};
