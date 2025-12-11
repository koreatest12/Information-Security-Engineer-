import time
def log_transaction(tx_id, status):
    with open('transaction_history/tx_log.txt', 'a') as f:
        f.write(f"{time.ctime()} | TX:{tx_id} | {status}\n")
