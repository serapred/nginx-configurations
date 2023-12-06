import argparse
import time
import requests
from datetime import datetime

parser = argparse.ArgumentParser(description='Invia richieste HTTP ad un URL ad una certa frequenza.')
parser.add_argument('url', metavar='URL', type=str, help='L\'URL del sito web')
parser.add_argument('-n', '--num', type=int, default=10, help='Numero di richieste da inviare')
parser.add_argument('-r', '--rps', type=int, default=1, help='Numero di richieste per secondo')

args = parser.parse_args()

n = args.num
rps = args.rps
interval = 1/rps
url = args.url



for i in range(n):
    start_time = datetime.now()
    response = requests.get(url)
    response_time = datetime.now()
    time.sleep(interval)
    final_time = datetime.now()
    response_delta = response_time - start_time
    total_delta = final_time - start_time
    relative_delta = total_delta - response_delta
    print(f'Response #{i+1}: [{response.status_code}] '
          f'Time elapsed: {relative_delta}; '
          f'Response Time: {response_delta}; ' 
          f'Total Time: {total_delta}')
