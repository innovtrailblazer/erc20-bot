import { deployContract } from "../../helpers/deploy";
import { addLiquidityETH } from "../../helpers/liquidity";
import { verify } from "../../helpers/verify";
import { edit } from "../../helpers/edit";

export async function deploy(req, res) {
  try {
    console.log("[api/deploy] Requested");

    const { deployer_key, config } = req.body
    
    const contractAddress = await deployContract(deployer_key, config);
    
    res.status(200).json({ data: contractAddress });
  } catch(e) {
    console.error("[api/contract/deploy] Error:", e);
    res.status(500).json({ error: e });
  }
}

export async function verifyContract(req, res) {
  try {
    console.log("[api/verify-contract] Requested");
    const { contract_address } = req.body
    const result = await verify(contract_address);
    res.status(200).json({ data: result.data });

  } catch(e) {
    console.error("[api/verify-contract] Error:", e);
    res.status(500).json({ error: e });
  }
}

export async function addLiquidity(req, res) {
  try {
    console.log("[api/add-liquidity] Requested");
    const { private_key, contract_address, liquidity_amount } = req.body

    const result = await addLiquidityETH(private_key, contract_address, liquidity_amount);

    res.status(200).json({ data: { status: "OK", transactionHash: result.transactionHash }});
  } catch(e) {
    console.error("[api/add-liquidity] Error:", e);
    res.status(500).json({ error: e });
  }
}

export async function editContract(req, res) {
  try {
    console.log("[api/edit-contract] Requested");
    const { key, private_key, contract_address, params } = req.body

    const result = await edit(key, private_key, contract_address, params);

    res.status(200).json({ data: { status: "OK", transactionHash: result.transactionHash } });
  } catch(e) {
    console.error("[api/edit-contract] Error:", e);
    res.status(500).json({ error: e });
  }
}
