from solscan import get_transaction_detail, get_address_transactions, get_address_data
from util import Local_Cache, save_json_to_file, read_json_from_file, parallel_functions
from pprint import pprint
import traceback
from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

def get_token_data_cache(token):
    token_data = Local_Cache.get(token)

    if not token_data:
        token_data = get_address_data(token)
        Local_Cache.set(token, token_data)

    return token_data



def process_transactions(transactions):
    tracking_address = Local_Cache.get("tracking_address")
    all_transactions = []
    for trans in transactions:
        try:
            transaction = get_transaction_detail(trans['txHash'])
            programs_involved = transaction.get("programs_involved")
            pump_fun_program_address = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
            raydium_program_address = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
            jupiter_program_address = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
            usd_coin = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
            sol_address = "So11111111111111111111111111111111111111112"
            sol_price = 170

            if pump_fun_program_address in programs_involved:
                transaction_type = None
                log_messages = transaction['logMessage']
                if 'Program log: Instruction: Buy' in log_messages:
                    transaction_type = "bought"

                if 'Program log: Instruction: Sell' in log_messages:
                    transaction_type = "sold"

                token = transaction['tokens_involved'][0]
                token_data = get_token_data_cache(token)
                token_name = token_data['metadata']['data'].get('name')
                if not token_name:
                    print(token_data)

                sol_bal_change = transaction['sol_bal_change']
                amount = next((bal['change_amount'] for bal in sol_bal_change if bal['address'] == tracking_address), None)
                usd_amount = None
                if amount:
                    amount = round(abs(amount / 1000000000), 3)
                    usd_amount = round(amount * sol_price)

                data = {"txHash": trans['txHash'], "type": transaction_type, "token_name": token_name,"sol_amount": amount, "usd_amount": usd_amount}
                all_transactions.append(data)

            elif jupiter_program_address in programs_involved or raydium_program_address in programs_involved:
                transaction_type = None
                tokens_involved = transaction['tokens_involved']

                token = next((token for token in tokens_involved if token != sol_address))
                amount = next((bal_change['change_amount'] for bal_change in transaction['sol_bal_change'] if
                               bal_change['address'] == tracking_address), None)

                if amount < 0:
                    transaction_type = "bought"
                else:
                    transaction_type = "sold"

                token_data = get_token_data_cache(token)
                token_name = token_data['metadata']['data'].get('name')

                usd_amount = None
                if amount:
                    amount = round(abs(amount / 1000000000), 4)
                    usd_amount = round(amount * sol_price)

                data = {"txHash": trans['txHash'], "type": transaction_type, "token_name": token_name,"sol_amount": amount, "usd_amount": usd_amount}
                all_transactions.append(data)
            else:
                pass

        except Exception as e:
            print(traceback.format_exc())
            print("something went wrong ", e)
    return all_transactions


def calculate_profit_or_loss_and_win_rate(transactions):
    text_result = ""
    # Initialize dictionaries to track total bought and sold amounts in USD
    total_bought = defaultdict(lambda: {'usd': 0})
    total_sold = defaultdict(lambda: {'usd': 0})

    # Process each transaction
    for transaction in transactions:
        type_ = transaction['type']
        token_name = transaction['token_name']
        usd_amount = transaction['usd_amount']

        if type_ in ['buy', 'bought']:
            total_bought[token_name]['usd'] += usd_amount
        elif type_ in ['sell', 'sold']:
            total_sold[token_name]['usd'] += usd_amount

    # Calculate profit or loss for each coin and total PnL
    results = {}
    total_pnl = 0
    total_trades = 0
    winning_trades = 0

    for token in set(total_bought.keys()).union(total_sold.keys()):
        bought_usd = total_bought[token]['usd']
        sold_usd = total_sold[token]['usd']

        # Calculate profit or loss
        profit_or_loss = sold_usd - bought_usd
        results[token] = {
            'profit_or_loss': profit_or_loss,
            'total_bought_usd': bought_usd,
            'total_sold_usd': sold_usd
        }
        total_pnl += profit_or_loss

        # Determine winning trades
        if profit_or_loss > 0:
            winning_trades += 1

        # Count total trades
        total_trades += 1

    # Calculate win rate
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
    else:
        win_rate = 0

    # Print the results
    for token, data in results.items():
        pnl = data['profit_or_loss']
        bought_usd = data['total_bought_usd']
        sold_usd = data['total_sold_usd']
        text_result += f"Token: {token}, Total Bought: {bought_usd:.2f} USD, Total Sold: {sold_usd:.2f} USD, Profit/Loss: {pnl:.2f} USD\n\n"

    text_result += f"Total Profit/Loss: {total_pnl:.2f} USD\n"
    text_result += f"Win Rate: {win_rate:.2f}%"
    return text_result

@app.get("/")
def home():
    return "this is the home page"


@app.get("/analyze/<tracking_address>")
def get_analysis(tracking_address):
    transactions = get_address_transactions(tracking_address)
    Local_Cache.set("tracking_address", tracking_address)
    batch_size = 100
    batches = [transactions[i:i + batch_size] for i in range(0, len(transactions), batch_size)]
    responses = parallel_functions(batches, process_transactions, max_workers=2)
    all_transactions = []

    for response in responses:
        all_transactions.extend(response)

    for transaction in all_transactions:
        if transaction['token_name'] == "USDT":
            all_transactions.remove(transaction)

    return calculate_profit_or_loss_and_win_rate(all_transactions)


if __name__ == '__main__':
    app.run()