from datetime import datetime
from time import sleep
from config import TOKEN, SPL_TOKEN_PROGRAM_ID
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature


class Solscan:
    client = Client("https://api.mainnet-beta.solana.com")

    def get_token_update_authority(self, pubkey: Pubkey) -> Pubkey:
        account_info = self.client.get_account_info(pubkey)
        print(account_info)
        update_authority_bytes = account_info.value.data[4:36]
        return Pubkey(update_authority_bytes)

    def find_deploy_transaction(self, deploy_account: Pubkey, token_pb: Pubkey) -> int:

        transaction_signatures = self.client.get_signatures_for_address(deploy_account, limit=1000).value
        found_token_creation = None
        start_ts = datetime.now()
        for transaction_sig in transaction_signatures:
            sleep(5)
            transaction = self.client.get_transaction(
                transaction_sig.signature, max_supported_transaction_version=0
            ).value.transaction
            accs = transaction.transaction.message.account_keys
            if (
                any("InitializeMint" in item for item in transaction.meta.log_messages)
                and token_pb in accs
                and SPL_TOKEN_PROGRAM_ID in accs
            ):
                print(transaction)
                end_ts = datetime.now()

                print(end_ts - start_ts)
                if found_token_creation:
                    print(f"Token was deployed in transaction: {transaction}")
                else:
                    print("Token deployment transaction not found.")
                return transaction


    def find_first_50_transactions(self, token_pb: Pubkey, initial_transaction: Signature):
        # Storage for unique buyers
        unique_buyers = {}

        # Start fetching transactions
        signatures = self.client.get_signatures_for_address(
            token_pb, before=initial_transaction, limit=1000
        ).value

        while signatures and len(unique_buyers) < 50:
            # Fetch full transaction details for each signature
            for signature_detail in signatures:
                # Get the full transaction
                transaction = self.client.get_transaction(
                    signature_detail.signature, max_supported_transaction_version=0
                ).value.transaction
                if transaction.meta.err:
                    continue
                # Extract token balances before and after the transaction
                pre_balances = [bal for bal in transaction.meta.pre_token_balances if bal.mint == token_pb]
                post_balances = [bal for bal in transaction.meta.post_token_balances if bal.mint == token_pb]
                # Map balances by owner
                pre_dict = {bal.owner: int(bal.ui_token_amount.amount) for bal in pre_balances}
                post_dict = {bal.owner: int(bal.ui_token_amount.amount) for bal in post_balances}
                # Identify changes in balances
                for owner, post_bal in post_dict.items():
                    pre_bal = pre_dict.get(owner, 0)
                    balance_change = post_bal - pre_bal
                    # Check if this is a positive change and the owner isn't already tracked
                    if balance_change > 0 and owner not in unique_buyers:
                        unique_buyers[owner] = post_bal
                        if len(unique_buyers) >= 50:
                            break

            if len(unique_buyers) >= 50:
                break

            # Move to the next batch of transactions
            last_signature = signatures[-1].signature
            sleep(5)
            print("Searching for transactions..")
            signatures = self.client.get_signatures_for_address(token_pb, before=last_signature, limit=1000).value

        return unique_buyers


# get_token_update_authority = slc.get_token_update_authority(token_pd)
# trans = slc.find_deploy_transaction(token_update_authority, token_pd)

slc = Solscan()
token_pd = Pubkey.from_string(TOKEN)
token_update_authority = Pubkey.from_string("4kkCwULQwpiEZh6W1vUwSWcgLUTzCsDuP1TEbzQYY9Dn")
initial_sig = Signature(
    "56Zqx7fiDVsdFJEGn54D5wKAD32QVDmySzLSVxqS86ADXwqib995oCpupLLaJzDYeJCayYTht37AXwwXHjWSErDw"
)

print(slc.find_first_50_transactions())