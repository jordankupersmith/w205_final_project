from datetime import timedelta, date, datetime
import urllib, json
import time
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

startTime = datetime.now()
args = int(sys.argv[1])
epoch = datetime.utcfromtimestamp(0)

conn = psycopg2.connect(database="blockchain", user="postgres", password="pass", host="localhost", port="5432")
cur = conn.cursor()



def daterange(start_date, end_date):
    for n in range(int ((end_date  - start_date).days)):
        yield start_date + timedelta(n)        

def unix_time_millis(d):
    dt = datetime(d.year, d.month, d.day)
    return (dt - epoch).total_seconds() * 1000.0
    

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

    
def get_timestamp(block_hash):
    time_data=block_variables['time']
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    time_data_utc=time_data -utc_offset
    return datetime.fromtimestamp(time_data_utc).strftime('%Y-%m-%d %H:%M:%S')
    

       
#####A blocks block hash always identifies a single block uniquely. A block also always has a specific block height. However, it is not always #the case that a specific block height can identify a single block. Rather, two or more blocks might compete for a single position in the #blockchain.
if __name__ == "__main__": 

    start_date = date(args, 1, 1)
    end_date = date(args, 12, 31)
    end_date1 = end_date + timedelta(days=1)
    date_count_list = []
    
    for single_date in daterange(start_date, end_date1):    
        day_ms = unix_time_millis(single_date)
        
        block_hashes = get_block_hashes(day_ms)
        day_tx_count = 0
        
        for i, block_hash in enumerate(block_hashes):
            block_variables=get_block_info(block_hash)
            hash_value=block_variables['hash']
            block_tx_count = block_variables['n_tx']
            block_tx_count_str=str(block_tx_count)
            height =str(block_variables['height'])
            timestamp = get_timestamp(block_hash)
            print "block {} of {} has a hash of {}, a height of {} and has {} transactions and was processed at {}".format(i, len(block_hashes), hash_value, height, block_tx_count, timestamp)
            day_tx_count += block_tx_count
            try:
                cur.execute("INSERT INTO blocks (hash_value, height, block_tx_count, timestamp) VALUES ('" + hash_value + "', '" + height + "', '" + block_tx_count_str + "', '" + timestamp + "')");
            except:
                pass
            conn.commit()
        print single_date, day_tx_count
        date_count_list.append((single_date, day_tx_count))
    
    print "\n\n========== DONE ==========\n\n"
    print date_count_list
conn.close()    
print "The script took", datetime.now() - startTime   
 
