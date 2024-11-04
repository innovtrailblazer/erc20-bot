import axios from 'axios';
import qs from 'qs';
import * as constants from './constants';
import fs from 'fs';
import path from 'path';

export const verify = (contractAddress) => {
  return new Promise((res, rej) => {
    fs.readdir(path.join(__dirname, '../contracts/generated/'), (err, files) => {
      files.forEach(file => {
        if(file.includes(contractAddress)) {
          const contractName = file.replace('.sol', '').slice(43);
          const source = fs.readFileSync(path.join(__dirname, '../contracts/generated/' + file), 'utf8');
          
          let data = qs.stringify({
            'apikey': constants.ETHERSCAN_API_KEY,
            'module': 'contract',
            'action': 'verifysourcecode',
            'sourceCode': source,
            'contractaddress': contractAddress,
            'codeformat': 'solidity-single-file',
            'contractname': contractName,
            'compilerversion': constants.SOLC_VERSION,
            'optimizationused': '0' 
          });
          
          let config = {
            method: 'post',
            maxBodyLength: Infinity,
            url: constants.ETHERSACN_API_URL,
            headers: { 
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            data : data
          };

          axios.request(config)
            .then(res)
            .catch(rej)
        }
      });
    });
  })
}
