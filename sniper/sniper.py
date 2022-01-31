import argparse

from os47.OS47 import OS47

parser = argparse.ArgumentParser(description="Snipe NFTs below x price")
parser.add_argument("--mainnet", action="store_true", help="Snipe on mainnet")
parser.add_argument("contract_address", type=str, help="contract/collection address")

args = parser.parse_args()
print(args)

os47 = OS47(args.contract_address, args.mainnet)
# os47.fire(397)
os47._get_listing_data(4)