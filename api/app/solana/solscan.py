from datetime import datetime
import logging
from time import sleep
from app.config import SOLANA_RPC_URL
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc import types
from solana.rpc.core import InvalidParamsMessage
from solana.exceptions import SolanaRpcException

logger = logging.getLogger("resources")


class TokenChainInfo:
    client = Client(SOLANA_RPC_URL)

    def __init__(self, token_address: str) -> None:
        self.token_pb = Pubkey.from_string(token_address)
        self.token_update_authority = None
        self.init_mint_sig = None

    def check_if_token(self) -> tuple[bool, str]:
        ans = self.client.get_token_supply(self.token_pb)
        if isinstance(ans, InvalidParamsMessage):
            return False, ans.message
        return True, "Token found"

    def get_token_update_authority(self) -> Pubkey:
        account_info = self.client.get_account_info(self.token_pb)
        print(account_info)
        update_authority_bytes = account_info.value.data[4:36]
        self.token_update_authority = Pubkey(update_authority_bytes)
        return Pubkey(update_authority_bytes)

    def collect_token_signatures(self):
        # Start fetching transaction signatures

        try:
            signatures = self.client.get_signatures_for_address(self.token_pb, limit=1000).value
        except SolanaRpcException as e:
            sleep(15)
            signatures = self.client.get_signatures_for_address(self.token_pb, limit=1000).value
        # Start timing
        start_ts = datetime.now()
        # Loop until no more signatures are found
        while signatures:
            logger.info("Getting signatures...")
            # Collect all valid signatures (no errors) from the current batch
            valid_signatures = [sig for sig in signatures if sig.err is None]
            # Yield the current batch of valid signatures
            yield valid_signatures

            # Get the last signature in the current batch to use as the 'before' parameter for the next batch
            last_signature = signatures[-1].signature
            # Fetch the next batch of signatures
            try:
                signatures = self.client.get_signatures_for_address(
                    self.token_pb, before=last_signature, limit=1000
                ).value
            except SolanaRpcException as e:
                sleep(15)
                signatures = self.client.get_signatures_for_address(
                    self.token_pb, before=last_signature, limit=1000
                ).value

        # End timing and print total time
        end_ts = datetime.now()
        logger.info(end_ts - start_ts)

    def find_first_50_transactions(self, signatures):
        # Storage for unique buyers
        unique_buyers = {}
        # Start fetching transactions
        for sig in signatures:
            signature = Signature.from_string(sig)
            # Get the full transaction
            try:
                transaction = self.client.get_transaction(
                    signature, max_supported_transaction_version=0
                ).value.transaction
            except SolanaRpcException as e:
                sleep(15)
                transaction = self.client.get_transaction(
                    signature, max_supported_transaction_version=0
                ).value.transaction
            if transaction.meta.err:
                continue
            signer = transaction.transaction.message.account_keys[0]
            # Extract token balances before and after the transaction
            pre_balances = [bal for bal in transaction.meta.pre_token_balances if bal.mint == self.token_pb]
            post_balances = [bal for bal in transaction.meta.post_token_balances if bal.mint == self.token_pb]
            # Map balances by owner
            pre_dict = {bal.owner: int(bal.ui_token_amount.amount) for bal in pre_balances}
            post_dict = {bal.owner: int(bal.ui_token_amount.amount) for bal in post_balances}
            # Identify changes in balances
            for owner, post_bal in post_dict.items():
                pre_bal = pre_dict.get(owner, 0)
                balance_change = post_bal - pre_bal
                # Check if this is a positive change and the owner isn't already tracked
                if balance_change > 0 and owner not in unique_buyers and str(signer) == str(owner):
                    unique_buyers[owner] = post_bal
                    if len(unique_buyers) >= 50:
                        break
            logger.info(f"Found {len(unique_buyers)} holders...")
            if len(unique_buyers) >= 50:
                break
        return unique_buyers

    def get_current_holders_balances(self, holders):
        opts = types.TokenAccountOpts(mint=self.token_pb, encoding="base64")
        current_balances = []
        for holder_address in holders:
            pk = Pubkey.from_string(holder_address)
            current_amount = 0
            try:
                token_accounts = self.client.get_token_accounts_by_owner(pk, opts=opts)
            except SolanaRpcException as e:
                sleep(15)
                token_accounts = self.client.get_token_accounts_by_owner(pk, opts=opts)
            for token_acc in token_accounts.value:
                print(token_acc.pubkey)
                try:
                    current_amount += int(
                        self.client.get_token_account_balance(token_acc.pubkey).value.amount
                    )
                except SolanaRpcException as e:
                    sleep(15)
                    current_amount += int(
                        self.client.get_token_account_balance(token_acc.pubkey).value.amount
                    )
            current_balances.append(current_amount)
        return current_balances
