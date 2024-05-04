from datetime import datetime
from time import sleep
from app.solana.config import INIT_MINT_COMMAND, SRC_URL, TOKEN, SPL_TOKEN_PROGRAM_ID
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc import types

from solana.exceptions import SolanaRpcException


class TokenChainInfo:
    client = Client(SRC_URL)

    def __init__(self, token_address: str) -> None:
        self.token_pb = Pubkey.from_string(token_address)
        self.token_update_authority = None
        self.init_mint_sig = None

    def get_token_update_authority(self) -> Pubkey:
        account_info = self.client.get_account_info(self.token_pb)
        print(account_info)
        update_authority_bytes = account_info.value.data[4:36]
        self.token_update_authority = Pubkey(update_authority_bytes)
        return Pubkey(update_authority_bytes)

    def find_deploy_transaction(self) -> Signature:

        transaction_signatures = self.client.get_signatures_for_address(
            self.token_update_authority, limit=1000
        ).value
        found_token_creation = None
        start_ts = datetime.now()
        for transaction_sig in transaction_signatures:
            try:
                transaction = self.client.get_transaction(
                    transaction_sig.signature, max_supported_transaction_version=0
                ).value.transaction
            except SolanaRpcException as e:
                sleep(5)
                transaction = self.client.get_transaction(
                    transaction_sig.signature, max_supported_transaction_version=0
                ).value.transaction
            accs = transaction.transaction.message.account_keys
            if (
                any(INIT_MINT_COMMAND in item for item in transaction.meta.log_messages)
                and self.token_pb in accs
                and SPL_TOKEN_PROGRAM_ID in accs
            ):
                print(transaction)
                end_ts = datetime.now()

                print(end_ts - start_ts)
                if found_token_creation:
                    print(f"Token was deployed in transaction: {transaction}")
                else:
                    print("Token deployment transaction not found.")
                self.init_mint_sig = transaction_sig.signature
                return self.init_mint_sig

    def collect_token_signatures(self):
        token_signatures = []
        start_ts = datetime.now()
        # Start fetching transaction signatures
        signatures = self.client.get_signatures_for_address(
            self.token_pb, limit=1000, until=initial_sig
        ).value
        print(f"{signatures[0].signature} ... {signatures[-1].signature}")
        # Loop until no more signatures are found
        while signatures:
            # Collect all signatures from the current batch
            for signature_detail in signatures:
                if signature_detail.err is None:
                    token_signatures.append(signature_detail.signature)
            # Get the last signature in the current batch to use as the 'before' parameter for the next batch
            last_signature = signatures[-1].signature
            # Fetch the next batch of signatures
            signatures = self.client.get_signatures_for_address(
                self.token_pb, before=last_signature, limit=1000, until=initial_sig
            ).value
            print(datetime.now())
            print(len(token_signatures))
        end_ts = datetime.now()
        print(end_ts - start_ts)
        print(len(token_signatures))

    def find_first_50_transactions(self):
        # Storage for unique buyers
        unique_buyers = {}

        # Start fetching transactions
        signatures = self.client.get_signatures_for_address(self.token_pb, limit=1000).value

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
                pre_balances = [
                    bal for bal in transaction.meta.pre_token_balances if bal.mint == self.token_pb
                ]
                post_balances = [
                    bal for bal in transaction.meta.post_token_balances if bal.mint == self.token_pb
                ]
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
            print("Searching for transactions..")
            signatures = self.client.get_signatures_for_address(
                self.token_pb, before=last_signature, limit=1000
            ).value
        self.holders = unique_buyers
        return unique_buyers

    def get_current_holders_balances(self):
        opts = types.TokenAccountOpts(mint=self.token_pb, encoding="base64")

        for pk, amount in self.holders.items():
            print(pk)
            current_amount = 0
            try:
                token_accounts = self.client.get_token_accounts_by_owner(pk, opts=opts)
            except SolanaRpcException as e:
                sleep(5)
                token_accounts = self.client.get_token_accounts_by_owner(pk, opts=opts)
            for token_acc in token_accounts.value:
                print(token_acc.pubkey)
                try:
                    current_amount += int(
                        self.client.get_token_account_balance(token_acc.pubkey).value.amount
                    )
                except SolanaRpcException as e:
                    sleep(5)
                    current_amount += int(
                        self.client.get_token_account_balance(token_acc.pubkey).value.amount
                    )
            print(current_amount)
