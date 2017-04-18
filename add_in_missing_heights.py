from datetime import timedelta, date, datetime
import urllib, json
import time
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

startTime = datetime.now()

epoch = datetime.utcfromtimestamp(0)



# def daterange(start_date, end_date):
    # for n in range(int ((end_date  - start_date).days)):
        # yield start_date + timedelta(n)        

# def unix_time_millis(d):
    # dt = datetime(d.year, d.month, d.day)
    # return (dt - epoch).total_seconds() * 1000.0
    


def get_missing_height(height):
    url = "https://blockchain.info/block-height/{:.0f}?format=json"
   
    connection_test=True
    m=0
    while connection_test == True and m < 500:
        try:
            print "Connecting to blockchain.info..."
            response = urllib.urlopen(url.format(height))
            data = json.loads(response.read())
            connection_test=False
            return data['blocks']
            break              
        except:
            print "Connection not working trying again in 20 seconds"
            time.sleep(20)
            m=m + 1
            continue

def get_block_hashes(height):
    block_list = get_missing_height(height)
    print "{} blocks in list for height {:.0f}".format(len(block_list), height)
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
    
    
conn = psycopg2.connect(database="blockchain", user="postgres", password="pass", host="localhost", port="5432")
cur = conn.cursor()


cur.execute("SELECT cast(height as int) FROM blocks ORDER BY cast(height as int)");
data = cur.fetchall()

#conn.commit()
cur.execute("SELECT max(cast(height as int)) FROM blocks");
max_value = cur.fetchall()

max_value=[i[0] for i in max_value]
max_value1=max_value[0] 



#conn.commit()


height_list=[]
for i in data:
    
    height_list.append(i[0])
    

missing_height=[]    
j=0
for i in range(0, max_value1 + 1):
    if i not in height_list:
        missing_height.append(i)
        #print i
        j=j+1
    else:
        pass
        

#print missing_height
print "number of missing heights:", j



       
#####A blocks block hash always identifies a single block uniquely. A block also always has a specific block height. However, it is not always #the case that a specific block height can identify a single block. Rather, two or more blocks might compete for a single position in the #blockchain.
if __name__ == "__main__": 

  
    for h in missing_height:
        height=h    
          
            
        block_hashes = get_block_hashes(height)
            
        #day_tx_count = 0
        for i, block_hash in enumerate(block_hashes):
            #print block_hash
            time.sleep(.1) ### putting this in just to give a bit of relief to the server so we def. get the data
            block_variables=get_block_info(block_hash)
            hash_value=block_variables['hash']
            block_tx_count = block_variables['n_tx']
            block_tx_count_str=str(block_tx_count)
            height =str(block_variables['height'])
            #indicates whether a block was orphaned or not. We are not interested in orphaned blocks.
            main_chain=str(block_variables['main_chain'])
            
            timestamp = get_timestamp(block_hash)
            print "block {} of {} has a hash of {}, a height of {}, has {} transactions, was processed at {} and main chain={}".format(i, len(block_hashes), hash_value, height, block_tx_count, timestamp, main_chain)
            
            if main_chain=="True":
                try:
                    
                    cur.execute("INSERT INTO blocks (hash_value, height, block_tx_count, timestamp) VALUES ('" + hash_value + "', '" + height + "', '" + block_tx_count_str + "', '" + timestamp + "')");
               
                except:
                    pass
            else:
                print "main chain false"
            conn.commit()
        
    
    print "\n\n========== DONE ==========\n\n"
    
conn.close()    
print "The script took", datetime.now() - startTime   
 
