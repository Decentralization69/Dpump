import requests
import json
import os
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig

load_dotenv()

def send_local_create_tx(name, symbol, description, image_url):
    base58_private_key = os.getenv('SOLANA_PRIVATE_KEY')
    solana_rpc_url = os.getenv('SOLANA_RPC_URL')
    
    if not base58_private_key:
        return False, "Error: Environment variable 'SOLANA_PRIVATE_KEY' is not set."
    
    if not solana_rpc_url:
        return False, "Error: Environment variable 'SOLANA_RPC_URL' is not set."

    signer_keypair = Keypair.from_base58_string(base58_private_key)

    mint_keypair = Keypair()

    form_data = {
        'name': name,
        'symbol': symbol,
        'description': description,
        'showName': 'true'
    }

    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        return False, f"Error: Failed to download image: {image_response.text}"

    file_content = image_response.content

    files = {
        'file': ('image.jpg', file_content, 'image/jpg')
    }

    metadata_response = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files)
    if metadata_response.status_code != 200:
        return False, f"Error: IPFS metadata storage failed: {metadata_response.text}"

    metadata_response_json = metadata_response.json()

    token_metadata = {
        'name': form_data['name'],
        'symbol': form_data['symbol'],
        'uri': metadata_response_json['metadataUri']
    }

    response = requests.post(
        "https://pumpportal.fun/api/trade-local",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'publicKey': str(signer_keypair.pubkey()),
            'action': 'create',
            'tokenMetadata': token_metadata,
            'mint': str(mint_keypair.pubkey()),
            'denominatedInSol': 'true',
            'amount': 0.001,
            'slippage': 10,
            'priorityFee': 0.0005,
            'pool': 'pump'
        })
    )

    mint_address = str(mint_keypair.pubkey())

    if response.status_code != 200:
        return False, f"Error: Create transaction failed: {response.text}"

    tx = VersionedTransaction(VersionedTransaction.from_bytes(response.content).message, [mint_keypair, signer_keypair])

    commitment = CommitmentLevel.Confirmed
    config = RpcSendTransactionConfig(preflight_commitment=commitment)
    txPayload = SendVersionedTransaction(tx, config)

    response = requests.post(
        url=solana_rpc_url,
        headers={"Content-Type": "application/json"},
        data=txPayload.to_json()
    )

    if response.status_code != 200:
        return False, f"Error: Transaction submission failed: {response.text}"

    txSignature = response.json()['result']
    
    token_url = f"https://pump.fun/{mint_address}"

    success_message = (
        f"🎉 New Token Created! 🚀\n"
        f"🌟 Name: {name}\n"
        f"💰 Symbol: {symbol}\n"
        f"📄 Description: {description}\n"
        f"🔗 View it here: {token_url}"
    )

    return True, success_message
