import { getGas, getWeb3 } from "./web3-helper";

const erc20ABI = require("../abis/ERC20.json");

export const edit = async (key, privateKey, contractAddress, params) => {
  const web3 = getWeb3(privateKey);
  const tokenContract = new web3.eth.Contract(erc20ABI, contractAddress);

  let tx;

  switch (key) {
    case "openTrading":
      tx = tokenContract.methods.openTrading();
      break;
    case "addExcludedWallet":
      tx = tokenContract.methods.addExcludedWallet(params["wallet"]);
      break;
    case "removeLimits":
      tx = tokenContract.methods.removeLimits();
      break;
    case "changeTax":
      tx = tokenContract.methods.changeTax(
        params["newBuyTax"],
        params["newSellTax"]
      );
      break;
  }

  const { gas: editGas, gasPrice: editGasPrice } = getGas(web3, tx, { from: web3.eth.defaultAccount });
  const txResult = await tx.send({ from: web3.eth.defaultAccount, gas: editGas, gasPrice: editGasPrice });

  return txResult;
};
