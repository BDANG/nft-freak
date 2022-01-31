'''
An simple script for reading etherscan-verified contracts and redeploying them to rinkeby

Run as python testnetter.py <contract_address>
'''


import json
import subprocess
import requests

def load_contract_source_code(contract_addr):
    url = f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_addr}'
    r = requests.get(url)
    data = json.loads(r.text)
    return data


def testnetter(contract_addr):
    pass
    # load source code from etherscan
    source_code = load_contract_source_code(contract_addr)

    # save the source code to a file
    with open('contract.sol', 'w') as f:
        pass

    # use hardhat to deploy
    # subprocess.call('npx hardhat')

    # use hardhat to verify
    subprocess.call('npx hardhat verify --network rinkeby --constructor-args arguments.js DEPLOYED_CONTRACT_ADDRESS', shell=True)