import { getGas, getWeb3 } from "./web3-helper";
import { bigMul } from "./utils";
import fs from "fs";
import path from "path";
import solc from "solc";

export const deployContract = async (privateKey, config) => {
  const {
    token_name,
    token_symbol,
    token_decimal,
    token_supply,
    buy_tax,
    sell_tax,
    fee_recipient,
    max_txn_amount,
  } = config;

  const contractTemplatePath = path.join(
    __dirname,
    "../contracts/contract-template.sol"
  );
  const contractTemplate = fs.readFileSync(contractTemplatePath, "utf8");

  const contractName = token_name.replace(/\s/g, "");

  const generatedContract = contractTemplate
    .replace("{contractName}", contractName)
    .replace("{name}", token_name)
    .replace("{symbol}", token_symbol)
    .replace("{decimals}", token_decimal)
    .replaceAll("{totalSupply}", bigMul(token_supply, 10 ** token_decimal))
    .replace("{buyTax}", buy_tax)
    .replace("{sellTax}", sell_tax)
    .replace("{feeReceiverWallet}", fee_recipient);

  const web3 = getWeb3(privateKey);

  const contractFileName = contractName + ".sol";

  const input = {
    language: "Solidity",
    sources: {},
    settings: {
      outputSelection: {
        "*": {
          "*": ["abi", "evm.bytecode.object"],
        },
      },
    },
  };

  input.sources[contractFileName] = {
    content: generatedContract,
  };

  const compiledContract = JSON.parse(solc.compile(JSON.stringify(input)));
  console.log(compiledContract, contractFileName, contractName);
  const contractABI =
    compiledContract.contracts[contractFileName][contractName].abi;
  const contractBytecode =
    compiledContract.contracts[contractFileName][contractName].evm.bytecode
      .object;
  const contract = new web3.eth.Contract(contractABI);

  const tx = contract.deploy({ data: "0x" + contractBytecode, arguments: [] });
  const { gas, gasPrice } = getGas(web3, tx);

  const deployed = await tx.send({
    gas,
    gasPrice,
    from: web3.eth.defaultAccount,
  });

  fs.writeFile(
    path.join(
      __dirname,
      "../contracts/generated/" +
        deployed.options.address +
        "-" +
        contractName +
        ".sol"
    ),
    generatedContract,
    (err) => {
      if (err) throw err;
      console.log("File is created successfully.");
    }
  );

  return deployed.options.address;
};
