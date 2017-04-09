from datetime import timedelta, date, datetime
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
            print "Connecting to blockchain.info..."
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

def get_latest_block_from_table():
    
    
def get_timestamp(block):
    time_data = block['time']
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    time_data_utc=time_data -utc_offset
    return datetime.fromtimestamp(time_data_utc).strftime('%Y-%m-%d %H:%M:%S')
    

       
#####A blocks block hash always identifies a single block uniquely. A block also always has a specific block height. However, it is not always #the case that a specific block height can identify a single block. Rather, two or more blocks might compete for a single position in the #blockchain.
if __name__ == "__main__": 

    print "hello"
    block = get_latest_block_from_chain()
    block_hash = block['hash']
    height = block['height']
    num_tx = len(block['txIndexes'])
    ts = get_timestamp(block)

    print block_hash, height, num_tx, ts