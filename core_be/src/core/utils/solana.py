import requests
from decimal import Decimal

from asyncstdlib import enumerate
from channels.db import database_sync_to_async
from django.conf import settings
from solana.rpc.websocket_api import connect
from solana.publickey import PublicKey
from ...transaction.models import TransferTransaction as TransferTransactionModel

async def client(websocket_url):
	async with connect(websocket_url) as websocket:
		await websocket.logs_subscribe(filter_=	{"mentions": [settings.SOLANA_ADDRESS_WALLET]})
		first_resp = await websocket.recv()
		subscription_id = first_resp.result
		async for idx, msg in enumerate(websocket):
			signature = msg.result.value.signature
			txn_status, block_time, slot, sender_address, receiver_address, action, status, amount = get_data_from_solscan(signature=signature)
			if txn_status == "finalized":
				try: 
					await get_transaction(signature)
				except:
					await save_transaction(signature,block_time,slot,sender_address,receiver_address,action,status,amount)
		await websocket.logs_unsubscribe(subscription_id)

def get_data_from_solscan(signature):
	response = requests.get(f"{settings.SOLANA_API}/transaction?tx={signature}").json()
 	# response = requests.get(f"https://api-devnet.solscan.io/transaction?tx={signature}").json()

	txn_status = response.get("txStatus")
	block_time, slot, sender_address, receiver_address, action, status, amount, token_address= None, None, None, None, None, None, None, None
 
	if txn_status == "finalized":
		block_time = response.get("blockTime")
		slot = response.get("slot")
		main_actions = response.get("mainActions")[0]
		main_actions_data = main_actions.get("data")
		action = main_actions.get("action")
		status = response.get("status")
		amount = Decimal(main_actions_data.get("amount"))
		if action == "sol-transfer":
			sender_address = main_actions_data.get("source")
			receiver_address = main_actions_data.get("destination")
			amount = amount / 10**9
		else:	# action == "spl-transfer"
			sender_address = main_actions_data.get("source_owner")
			receiver_address = main_actions_data.get("destination_owner")
			token = main_actions_data.get("token")
			token_address = token.get("address")
			token_decimals = token.get("decimals")
			amount = amount / 10**token_decimals
	return txn_status, block_time, slot, sender_address, receiver_address, action, status, amount, token_address

@database_sync_to_async
def save_transaction(signature, block_time, slot, sender_address, receiver_address, action, status, amount, token_address):
    TransferTransactionModel.objects.create(
		signature=signature, 
		block_time=block_time, 
		slot=slot,
		sender=sender_address,
		receiver=receiver_address,
		action=action,
		status=status,
		amount=amount,
  		token_address=token_address)
    
@database_sync_to_async
def get_transaction(signature):
    TransferTransactionModel.objects.get(
		signature=signature
	)
    
def is_on_curve(address):
 	return PublicKey._is_on_curve(address)