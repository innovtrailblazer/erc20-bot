import { NumToBn } from './utils';
import { getDeadline, getGas, getWeb3 } from './web3-helper';
import * as constants from './constants';

import uniswapRouter02ABI from '../abis/UniswapRouter02.json';
import erc20ABI from '../abis/ERC20.json';

export const addLiquidityETH = async (privateKey, contractAddress, liquidityAmount) => {
  const web3 = getWeb3(privateKey);
  const tokenAmount = NumToBn(liquidityAmount['token_amount']).toString();
  const ethAmount = NumToBn(liquidityAmount['eth_amount']).toString();
  
  const tokenContract = new web3.eth.Contract(erc20ABI, contractAddress);
  const allowTx = tokenContract.methods.approve(constants.UNISWAP_ADDRESS, tokenAmount);
  const { gas: allowGas, gasPrice: allowGasPrice } = getGas(
    web3, 
    allowTx, 
    { 
      from : web3.eth.defaultAccount 
    }
  );
  await allowTx.send(
    { 
      from: web3.eth.defaultAccount, 
      gas: allowGas, 
      gasPrice: allowGasPrice 
    }
  );

  const uniswapContract = new web3.eth.Contract(uniswapRouter02ABI, constants.UNISWAP_ADDRESS);
  
  const uniTx = uniswapContract.methods.addLiquidityETH(
    contractAddress, 
    tokenAmount, 
    0, 
    0, 
    web3.eth.defaultAccount, 
    await getDeadline()
  );
  
  const { gas: uniGas, gasPrice: uniPrice } = getGas(
    web3, 
    uniTx, 
    { 
      value: ethAmount, 
      from: web3.eth.defaultAccount 
    }
  );

  const txResult = await uniTx.send(
    { 
      value: ethAmount, 
      from: web3.eth.defaultAccount, 
      gas: uniGas, 
      gasPrice: uniPrice 
    }
  );

  return txResult;
}