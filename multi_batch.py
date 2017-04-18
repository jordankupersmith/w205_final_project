import multiprocessing
import time
import urllib, json
import sys
import threading
import random
import argparse
import pprint 

from datetime import timedelta, date, datetime
from google.cloud import bigquery

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

dataset_name = "w205_final_project"
table_name = "blockchain_copy_3"
num_threads = 100
mode = "bigquery"

def daterange(start_date, end_date):
    for n in range(int ((end_date  - start_date).days)):
        yield start_date + timedelta(n)        

def unix_time_millis(date):
    d = date[0]
    dt = datetime(d.year, d.month, d.day)
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def get_day_blocks(day_ms):
    url = "https://blockchain.info/blocks/{:.0f}?format=json"
    connection_test=True
    m=0
    while connection_test == True and m < 500:
        try:
            response = urllib.urlopen(url.format(day_ms))
            data = json.loads(response.read())
            connection_test=False
            return data['blocks']
            break              
        except Exception as e:
            sleep_time = random.randrange(1,10)
            if m >=5:
                print e, "\nConnection not working trying again in {} seconds. Attempt number {}".format(sleep_time, m)
            time.sleep(sleep_time)
            m=m + 1
            continue

def get_day_block_hashes(day_ms):
    block_list = get_day_blocks(day_ms)
    block_hash_list = []
    for block in block_list:
        block_hash_list.append(block['hash'])
    return block_hash_list


def get_block_info(block_hash):
    url = "https://blockchain.info/rawblock/{0}"
    connection_test=True
    m=0
    while connection_test == True and m < 500:
        try:
            response = urllib.urlopen(url.format(block_hash))
            response_str = response.read()
            block_variables = json.loads(response_str)
            connection_test=False
            return block_variables
            break              
        except Exception as e:
            sleep_time = random.randrange(1,10)
            if m >= 5:
                print e, "\nConnection not working trying again in {} seconds. Attempt number {}".format(sleep_time, m)
            time.sleep(sleep_time)
            m=m + 1
            continue 

def get_timestamp(block):
    time_data = block['time']
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    time_data_utc=time_data -utc_offset
    return datetime.fromtimestamp(time_data_utc).strftime('%Y-%m-%d %H:%M:%S')    

def write_blocks_to_table(blocks):
    m = 0
    noErrors = False
    if mode is "bigquery":
        while not noErrors and m <= 5:
            bigquery_client = bigquery.Client()
            dataset = bigquery_client.dataset(dataset_name)
            table = dataset.table(table_name)

            # Reload the table to get the schema.
            table.reload()
            errors = table.insert_data(blocks)

            if not errors:
                print('Loaded {} rows into {}:{}'.format(len(blocks), dataset_name, table_name))
                noErrors = True
            else:
                # may introduce duplicates, be sure to dedupe
                print('Errors:')
                pprint(errors)
                print("retrying")

    else :
        # postgres mode
        for block in blocks:
            (hash_value, height, block_tx_count, timestamp) = block
            block_tx_count_str = str(block_tx_count)
            try:
                cur.execute("INSERT INTO blocks (hash_value, height, block_tx_count, timestamp) VALUES ('" + hash_value + "', '" + height + "', '" + block_tx_count_str + "', '" + timestamp + "')");
            except:
                pass
            conn.commit()

def date_block_worker(date):
    print "got " , date
    day_ms = unix_time_millis(date)
    
    block_hashes = get_day_block_hashes(day_ms)
    day_tx_count = 0

    blocks = []
    for i, block_hash in enumerate(block_hashes):
        block_variables = get_block_info(block_hash)
        hash_value = block_variables['hash']
        block_tx_count = block_variables['n_tx']
        height = block_variables['height']
        timestamp = get_timestamp(block_variables)
        row = (hash_value, height, block_tx_count, timestamp)
        blocks.append((row),)

    if len(blocks) > 0:
        write_blocks_to_table(blocks)
    print "done", date

def date_handler(date_list, num_threads):
    p = multiprocessing.Pool(num_threads)
    res_dict = {}
    try:
        p.map(date_block_worker, date_list)

    except KeyboardInterrupt:
        # Allow ^C to interrupt from any thread.
        sys.stdout.write('\033[0m')
        sys.stdout.write('User Interupt\n')

if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start",  help="start date MM/DD/YYYY")
    parser.add_argument("-e", "--end", help="end date MM/DD/YYYY")
    parser.add_argument("-t", "--table", default = 'blockchain_copy_3', help="bigquery table to use")
    parser.add_argument("-d", "--dataset", default = 'w205_final_project', help="bigquery dataset to use")
    parser.add_argument("-m", "--mode", default = 'bigquery', help="mode to use: postgres or bigquery")
    parser.add_argument("-n", "--num_threads", type=int, help="number of threads to use")

    args = parser.parse_args()


    start_date = datetime.strptime(args.start, '%m/%d/%Y')
    end_date = datetime.strptime(args.end, '%m/%d/%Y')
    end_date1 = end_date + timedelta(days=1)
    table_name = args.table
    dataset_name = args.dataset
    num_threads = args.num_threads
    mode = args.mode


    dates = []

    for single_date in daterange(start_date, end_date1):
        dates.append((single_date,))

    print dates

    date_handler(dates, num_threads)