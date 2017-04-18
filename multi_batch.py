import multiprocessing
import time
import urllib, json
import sys
import threading
import random

from datetime import timedelta, date, datetime
from google.cloud import bigquery

DATASET = "w205_final_project"
TABLE = "blockchain_copy_3"
N_THREADS = 100

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
            # print "Connecting to blockchain.info..."
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
    # print "{} blocks in list for day {:.0f}".format(len(block_list), day_ms)
    block_hash_list = []
    for block in block_list:
        # print "getting hash"
        block_hash_list.append(block['hash'])
    return block_hash_list


def get_block_info(block_hash):
    url = "https://blockchain.info/rawblock/{0}"
    connection_test=True
    m=0
    while connection_test == True and m < 500:
        try:
            # print "Connecting to blockchain.info..."
            # print "getting block" , block_hash
            response = urllib.urlopen(url.format(block_hash))
            response_str = response.read()
            block_variables = json.loads(response_str)
            # print "got block"
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
    # dataset_name = "w205_final_project"
    # print "inside block len", len(blocks)
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.dataset(DATASET)
    table = dataset.table(TABLE)

    # Reload the table to get the schema.
    table.reload()
    # print blocks
    errors = table.insert_data(blocks)

    if not errors:
        print('Loaded {} rows into {}:{}'.format(len(blocks), DATASET, TABLE))
    else:
        print('Errors:')
        pprint(errors)


def date_block_worker(date):
    print "got " , date
    day_ms = unix_time_millis(date)
    
    block_hashes = get_day_block_hashes(day_ms)
    day_tx_count = 0

    blocks = []
    
    for i, block_hash in enumerate(block_hashes):
        block_variables = get_block_info(block_hash)
        # print block_variables
        hash_value = block_variables['hash']
        # print "hash_value", hash_value
        block_tx_count = block_variables['n_tx']
        # print "block_tx_count", block_tx_count
        # block_tx_count_str = str(block_tx_count)
        height = block_variables['height']
        # print "height", height
        timestamp = get_timestamp(block_variables)
        row = (hash_value, height, block_tx_count, timestamp)
        blocks.append((row),)
        # print "timestamp", timestamp
        # print "block {} of {} has a hash of {}, a height of {} and has {} transactions and was processed at {}".format(i, len(block_hashes), hash_value, height, block_tx_count, timestamp)

    # print "block len" , len(blocks)
    if len(blocks) > 0:
        write_blocks_to_table(blocks)
    print "done", date

def date_handler(date_list):
    # print date_list
    p = multiprocessing.Pool(N_THREADS)
    res_dict = {}
    try:
        p.map(date_block_worker, date_list)

    except KeyboardInterrupt:
        # Allow ^C to interrupt from any thread.
        sys.stdout.write('\033[0m')
        sys.stdout.write('User Interupt\n')

if __name__ == '__main__':

    start_date = date(2009, 1, 1)
    end_date = date(2009, 12, 31)
    # end_date = date(args, 12, 31)
    end_date1 = end_date + timedelta(days=1)
    dates = []

    for single_date in daterange(start_date, end_date1):
        dates.append((single_date,))

    print dates

    date_handler(dates)