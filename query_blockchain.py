from datetime import timedelta, date, datetime
import urllib, json

epoch = datetime.utcfromtimestamp(0)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def unix_time_millis(d):
    dt = datetime(d.year, d.month, d.day)
    return (dt - epoch).total_seconds() * 1000.0

def get_day_blocks(day_ms):
    url = "https://blockchain.info/blocks/{:.0f}?format=json"
    response = urllib.urlopen(url.format(day_ms))
    data = json.loads(response.read())
    return data['blocks']


def get_block_hashes(day_ms):
    block_list = get_day_blocks(day_ms)
    print "{} blocks in list for day {:.0f}".format(len(block_list), day_ms)
    block_hash_list = []
    for block in block_list:
        block_hash_list.append(block['hash'])
    return block_hash_list

def get_block_tx_count(block_hash):
    url = "https://blockchain.info/rawblock/{0}"
    response = urllib.urlopen(url.format(block_hash))

    data = json.loads(response.read())
    return data['n_tx']


if __name__ == "__main__": 

    start_date = date(2009, 1, 27)
    end_date = date(2009, 1, 28)
    
    date_count_list = []
    for single_date in daterange(start_date, end_date):
        day_ms = unix_time_millis(single_date)
        block_hashes = get_block_hashes(day_ms)
        day_tx_count = 0
        for i, block_hash in enumerate(block_hashes):
            block_tx_count = get_block_tx_count(block_hash)
            print "block {} of {} has {} transactions".format(i, len(block_hashes), block_tx_count)
            
            day_tx_count += block_tx_count
        print single_date, day_tx_count
        date_count_list.append((single_date, day_tx_count))

    print "\n\n========== DONE ==========\n\n"
    print date_count_list
