import requests
from time import sleep
from pprint import pprint

# import winsound


headers = {'accept': 'application/json, text/plain, */*', 'accept-language': 'en-US,en;q=0.9', 'cache-control': 'no-cache', 'origin': 'https://solscan.io', 'pragma': 'no-cache', 'priority': 'u=1, i', 'referer': 'https://solscan.io/', 'sec-ch-ua': '"Chromium";v="124", "Brave";v="124", "Not-A.Brand";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'sec-gpc': '1', 'sol-aut': 'EuSnaE1sTutcn=KQXyxB9dls0fK=v2PnxJIIvDAw', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}


def error_handler():
    print("Solscan error")
    sleep(5)
    pass  # winsound.MessageBeep(winsound.MB_ICONHAND)


def get_block_data(block_no):
    url = 'https://api.solscan.io/v2/block'

    params = {'block': block_no}

    # Check response status
    while True:
        response = requests.get(url, headers=headers, params=params)
        status_code = response.status_code
        response = response.json()

        if status_code == 200:
            print(response)
            if response['success'] == True:
                return response['data']
            else:
                return
        else:
            print(f"Request failed with status code: {status_code}")
            print(response.text)  # Print error message or response content
            error_handler()
        sleep(2)


def get_transactions(block_no, offset=0, size=40):
    all_transactions = []
    block_data = get_block_data(block_no)
    if not block_data:
        return all_transactions
    total_transactions = block_data['transactions_count']

    while True:
        print("Getting offset ", offset)
        url = 'https://api.solscan.io/v2/block/txs'

        # Check response status
        while True:
            params = {'block': f'{block_no}', 'offset': f'{offset}', 'size': f'{size}'}

            response = requests.get(url, headers=headers, params=params)
            status_code = response.status_code
            response = response.json()

            if status_code == 200:
                transactions = response['data']['transactions']
                all_transactions.extend(transactions)
                break
            else:
                error_handler()
                print(f"Request failed with status code: {status_code}")
                print(response.text)  # Print error message or response content

        if (offset + 40) >= total_transactions:
            return all_transactions
        offset += 40


def get_transaction_detail(tx):
    url = 'https://api.solscan.io/v2/transaction-v2'

    params = {'tx': tx}

    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            status_code = response.status_code

            if status_code == 200:
                response = response.json()
                return response['data']
            else:
                print(f"Request failed with status code: {status_code}")
                print(response.text)  # Print error message or response content
        except Exception as e:
            print("something went wrong ", e)
            error_handler()


def get_address_transactions(address):
    limit = 40
    offset = 0
    url = "https://api.solscan.io/v2/account/token/txs"
    all_transactions = []

    while True:
        try:
            params = {"address": address, "limit": limit, "offset": offset, "account_type": "account_main"}

            response = requests.get(url, params=params, headers=headers)
            status_code = response.status_code
            # Check response status
            if status_code == 200:
                response = response.json()
                transactions = response['data']['tx']['transactions']
                all_transactions.extend(transactions)
                has_next = response['data']['tx']['hasNext']
                if not has_next:
                    return all_transactions

                offset += 40
            else:
                print(f"Request failed with status code: {response.status_code}")
            print("Getting address transactions offset ", offset)
        except Exception as e:
            error_handler()
            print("something went wrong ", e)


def get_address_transaction_count(address):
    limit = 40
    offset = 0
    url = "https://api.solscan.io/v2/account/token/txs"
    all_transactions = []

    while True:
        try:
            params = {"address": address, "limit": limit, "offset": offset, "account_type": "account_main"}

            response = requests.get(url, params=params, headers=headers)
            status_code = response.status_code
            # Check response status
            if status_code == 200:
                response = response.json()
                transactions = response['data']['tx']['transactions']
                all_transactions.extend(transactions)
                has_next = response['data']['tx']['hasNext']
                if not has_next:
                    return all_transactions

                offset += 40
            else:
                print(f"Request failed with status code: {response.status_code}")
            print("Getting address transactions offset ", offset)
        except Exception as e:
            error_handler()
            print("something went wrong ", e)


def get_token_holders(token_address):
    url = 'https://api.solscan.io/v2/token/holders'
    limit = 40
    offset = 0
    all_holders = []

    while True:
        params = {'token': token_address, 'offset': offset, 'size': limit}

        response = requests.get(url, params=params, headers=headers)
        status_code = response.status_code
        # Check response status
        if status_code == 200:
            response = response.json()
            total_holders = response['data']['total']
            holders = response['data']['result']
            all_holders.extend(holders)
            if len(all_holders) == total_holders:
                return all_holders

            offset += 40
        else:
            print(f"Request failed with status code: {response.status_code}")
            error_handler()
        print("Getting token holders offset ", offset)


def get_tokens_in_address(address):
    url = f'https://api.solscan.io/v2/account/v2/tokens?address={address}'

    # Check response status
    while True:
        response = requests.get(url, headers=headers)
        status_code = response.status_code

        if status_code == 200:
            response = response.json()
            if response['success'] == True:
                return response['data']
            else:
                return
        else:
            error_handler()
            print(f"Request failed with status code: {status_code}")
            print(response.text)  # Print error message or response content
        sleep(2)


def get_address_data(address):
    url = f'https://api.solscan.io/v2/account?address={address}'

    # Check response status
    while True:
        response = requests.get(url, headers=headers)
        status_code = response.status_code

        if status_code == 200:
            response = response.json()
            if response['success'] == True:
                return response['data']
            else:
                return
        else:
            error_handler()
            print(f"Request failed with status code: {status_code}")
            print(response.text)  # Print error message or response content
        sleep(2)
