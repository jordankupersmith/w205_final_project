import urllib, json
import time
import sys


from google.cloud import bigquery
from datetime import timedelta, date, datetime
from pprint import pprint as pp


EPOCH = datetime.utcfromtimestamp(0)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def unix_time_millis(d):
    dt = datetime(d.year, d.month, d.day)
    return (dt - EPOCH).total_seconds() * 1000.0

def get_day_blocks(day_ms):
    url = "https://blockchain.info/blocks/{:.0f}?format=json"
    connection_test=True
    m=0
    while connection_test == True and m < 500:
        try:
            print "Connecting to blockchain.info..."
            response = urllib.urlopen(url.format(day_ms))
            data = json.loads(response.read())
            connection_test=False
            return data['blocks']
            break              
        except:
            print "Connection not working trying again in 20 seconds"
            time.sleep(20)
            m=m + 1
            continue

def get_block_hashes(day_ms):
    block_list = get_day_blocks(day_ms)
    print "{} blocks in list for day {:.0f}".format(len(block_list), day_ms)
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
            print "Connecting to blockchain.info..."
            response = urllib.urlopen(url.format(block_hash))
            block_variables = json.loads(response.read())
            connection_test=False
            return block_variables
            break              
        except:
            print "Connection not working trying again in 20 seconds"
            time.sleep(20)
            m=m + 1
            continue 

def get_first_block_on_day(dt):
    day_ms = unix_time_millis(dt)
    day_blocks = get_day_blocks(day_ms)

    first_block_hash = day_blocks[0]['hash']
    return get_block_info(first_block_hash)

def get_bq_dataset(dataset_name):
    # Instantiates a client
    bigquery_client = bigquery.Client()

    # Prepares the new dataset
    dataset = bigquery_client.dataset(dataset_name)

    print('Dataset {} found.'.format(dataset.name))

    return dataset 

def get_timestamp_from_ms(ms):
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    time_ms_utc= ms - utc_offset
    return datetime.fromtimestamp(time_ms_utc).strftime('%Y-%m-%d %H:%M:%S')

def get_bq_table(dataset, table_name):
    bq_table = dataset.table(table_name)
    bq_table.reload()

    return bq_table

def write_block_to_bq(block, dataset, table):

    block_hash = block['hash']
    ts = get_timestamp_from_ms(block['time'])
    height = int(block['height'])
    num_tx = int(block['n_tx'])
    index = int(block['block_index'])

    rows = [
            (block_hash, ts, height, num_tx, index),
            ]


    errors = table.insert_data(rows)

    if not errors:
        print('Loaded 1 row into {}:{}'.format(dataset.name, table.name))
    else:
        print('Errors:')
        pp(errors)



if __name__ == '__main__':

    TABLE_NAME = 'blockchain_data'
    DATASET_NAME = 'w205_final_project'

    dataset = get_bq_dataset(DATASET_NAME)
    table = get_bq_table(dataset, TABLE_NAME)

    start_date = date(2017, 1, 1)
    end_date = date(2017, 1, 31)
    
    date_count_list = []
    for single_date in daterange(start_date, end_date):
        
        day_ms = unix_time_millis(single_date)
        
        block_hashes = get_block_hashes(day_ms)
        day_tx_count = 0
        
        for i, block_hash in enumerate(block_hashes):
            block = get_block_info(block_hash)
            write_block_to_bq(block, dataset, table)

        date_count_list.append((single_date, day_tx_count))
    
    print "\n\n========== DONE ==========\n\n"
    print date_count_list

print "The script took", datetime.now() - startTime   
 


