require('dotenv').config();

var contractApiRouter = require('./api/contract.router');

var errorHandler = require('../helpers/http-error-handler');

const route = (app) => {
  app.use('/api', contractApiRouter);
  // global error handler
  app.use(errorHandler);
}

module.exports = route;