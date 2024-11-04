
const express = require('express');
const router = express.Router();
const controller = require('../../controllers/api/contract.controller');

router.post('/deploy', controller.deploy);
router.post('/add-liquidity', controller.addLiquidity);
router.post('/edit-contract', controller.editContract);
router.post('/verify-contract', controller.verifyContract);

module.exports = router;
