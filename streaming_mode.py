from datetime import timedelta, date, datetime
from google.cloud import bigquery

import urllib, json
import time
import sys

startTime = datetime.now()
epoch = datetime.utcfromtimestamp(0)

def get_latest_block_from_chain():
    url = "https://blockchain.info/latestblock"
    connection_test=True
    m=0
    while connection_test == True and m < 500:
        try:
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            connection_test=False
            return data
            break              
        except:
            print "Connection not working trying again in 2 seconds"
            time.sleep(2)
            m=m + 1
            continue

def get_latest_block_hash_from_table(table_name):
    client = bigquery.Client()
    query = "SELECT hashvalue FROM `w205_final_project.{}` order by timestamp desc LIMIT 1".format(table_name)
    query_results = client.run_sync_query(query)
    query_results.use_legacy_sql = False
    query_results.run()

    page_token = None

    rows, total_rows, page_token = query_results.fetch_data(
        max_results=10,
        page_token=page_token)
    return rows[0][0]

def write_block_to_table(block, table_name):
    dataset_name = "w205_final_project"
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.dataset(dataset_name)
    table = dataset.table(table_name)

    # Reload the table to get the schema.
    table.reload()

    block_hash = block['hash']
    height = block['height']
    num_tx = len(block['txIndexes'])
    ts = get_timestamp(block)

    row =  ([block_hash, height, num_tx, ts],)
    errors = table.insert_data(row)

    if not errors:
        print('Loaded 1 row into {}:{}'.format(dataset_name, table_name))
    else:
        print('Errors:')
        pprint(errors)


def get_timestamp(block):
    time_data = block['time']
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    time_data_utc=time_data -utc_offset
    return datetime.fromtimestamp(time_data_utc).strftime('%Y-%m-%d %H:%M:%S')
    

       
#####A blocks block hash always identifies a single block uniquely. A block also always has a specific block height. However, it is not always #the case that a specific block height can identify a single block. Rather, two or more blocks might compete for a single position in the #blockchain.
if __name__ == "__main__": 

    table_name = sys.argv[1]
    print "Table name:", table_name
    latest_chain_block = get_latest_block_from_chain()
    latest_chain_hash = latest_chain_block['hash']

    latest_table_hash = get_latest_block_hash_from_table(table_name)

    print "Most recent on chain: ", latest_chain_hash
    print "Most recent in table: ", latest_table_hash

    if latest_chain_hash != latest_table_hash:
        print "writing ", latest_chain_hash, "to ", table_name
        write_block_to_table(latest_chain_block, table_name)
    else:
        print table_name, "is up to date"

    while True:
        print "Sleeping for 5 min..."
        time.sleep(5 * 60) # sleep 5 min

        new_block = get_latest_block_from_chain()
        new_hash = new_block['hash']

        if new_hash != latest_chain_hash:
            print "got a new block! {}".format(new_hash)
            write_block_to_table(new_block, table_name)
            latest_chain_hash = new_hash

