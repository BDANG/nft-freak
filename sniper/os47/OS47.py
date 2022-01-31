from web3 import Web3
import json
import os
import pathlib
import math
import requests

ZERO = '0x0000000000000000000000000000000000000000'

class OS47:
    def __init__(self, contract_addr, mainnet=False) -> None:
        self.contract_addr = contract_addr
        self.mainnet = mainnet

        network = 'mainnet' if mainnet else 'rinkeby'
        provider = f'https://{network}.infura.io/v3/582b184a37d6467180f70922b5d6f1ed'
        self.w3 = Web3(Web3.HTTPProvider(provider))

        with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'data', 'wyvernABI.json'), 'r') as f:
            abi = json.load(f)
        self.wyvernAddress = '0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b' if mainnet else '0x5206e78b21Ce315ce284FB24cf05e0585A93B1d9'
        self.wyvern = self.w3.eth.contract(address=self.wyvernAddress, abi=abi)

        self.api_url = 'https://api.opensea.io/api/v1' if mainnet else 'https://rinkeby-api.opensea.io/api/v1'

    def find_targets(self, price):
        pass

    def fire(self, token_id):
        # load signer
        listing_data = self._get_listing_data(token_id)

        # send the transaction
        txn = self._build_txn()

        # transaction_with_key(txn)

    def _construct_args(self, buyer_address, seller_address, price):
        # https://rinkeby.etherscan.io/tx/0x582ee7c0dc8233686d0a9b3a13cb5be7ec0174abd6f0bdf45b71ab66505be466
        addrs = [
            self.wyvernAddress,  # exchange
            buyer_address,  # maker
            seller_address, # taker
            ZERO,  # ZERO, addr[3] (fee recipient)
            self.contract_addr,
            ZERO,
            ZERO,
            self.wyvernAddress,
            seller_address,
            ZERO,
            ZERO,  # fee recipient
            self.contract_addr,
            ZERO,
            ZERO,
        ]
        assert len(addrs) == 14

        uints = [
            0,  # makerRelayerFee, TODO: royalty? 250 = 2.5%?
            0,  # takerRelayerFee
            0,  # makerProtocolFee
            0,  # takerProtocolFee
            Web3.toWei(price, 'ether'),
            0,
            123,  # TODO: timestamp?
            0,
            123,  # TODO: big number,
            0,  # TODO: 250 = 2.5%?
            0,
            0,
            0,
            Web3.toWei(price, 'ether'),
            0,
            123,  # TODO: timestamp?
            123,  # TODO: tiemstamp?
            123,  # TODO: big number, salt??
        ]
        assert len(uints) == 18

        feeMethods = [
            1,
            0,
            0,
            0,
            1,
            1,
            0,
            0
        ]
        assert len(feeMethods) == 8

        vs = [
            28,
            28
        ]
        assert len(vs) == 2

        rssMetadata = [
            ZERO,  # TODO: buyer signature r
            ZERO,  # TODO: buyer signature s
            ZERO,  # TODO: seller signature r
            ZERO,  # TODO: seller signature s
        ]
        assert len(rssMetadata) == 5
        return {
            'addrs': addrs,
            'uints': uints,
            'feeMethods': feeMethods,
            'calldataBuy': '0x23b872dd0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c084683a656d1cd06e80fb68afef365ca97f93eb0000000000000000000000000000000000000000000000000000000000000004',
            'calldataSell': '0x23b872dd0000000000000000000000001651700c498a5b77a87df00d7364c2ed22afca2b00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004',
            'replacementPatternBuy': '0x00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
            'replacementPatternSell': '0x000000000000000000000000000000000000000000000000000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0000000000000000000000000000000000000000000000000000000000000000',
            'staticExtractdataBuy': None,
            'staticExtratdataSell': None,
            'vs': vs,
            'rssMetadata': rssMetadata
        }

    def _build_txn(self, price):
        args = self._contruct_args(price)
        transaction = {
            'from': '',
            'value': Web3.toWei(price, 'ether'),
            'maxPriorityFeePerGas': Web3.toWei(3, 'gwei'),
            'maxFeePerGas': Web3.toWei(6, 'gwei')
        }
        atomicMatch = self.wyvern.functions.atomicMatch_(
            args['addrs'], args['uints'], args['feeMethods'],
            args['calldataBuy'], args['calldataSell'],
            args['replacementPatternBuy'], args['replacementPatternSell'],
            args['staticExtradataBuy'], args['staticExtradataSell'],
            args['vs'], args['rssMetadata']
        )
        gas_estimate = atomicMatch.estimateGas(transaction)
        transaction['gas'] = math.floor(gas_estimate * 1.25)
    
    def _get_listing_data(self, token_id):
        url = f'{self.api_url}/asset/{self.contract_addr}/{token_id}'
        print(url)
        r = requests.get(url)
        # TODO: reliable 200?
        result = r.json()
        orders = sorted(result['orders'], key=lambda order: order['created_date'])
        print(orders[-1])