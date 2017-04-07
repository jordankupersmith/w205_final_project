#https://blockchain.info/charts/market-price?timespan=all&format=json
####we must pull in from two time formats because we only get price data every other day more than 2 years ago
from datetime import timedelta, date, datetime
import urllib, json
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(database="blockchain", user="postgres", password="pass", host="localhost", port="5432")
cur = conn.cursor()

epoch = datetime.utcfromtimestamp(0)



def convert_time(mydict):
    time_data=mydict
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    time_data_utc=time_data -utc_offset
    
    return datetime.fromtimestamp(time_data_utc).strftime('%Y-%m-%d')

price_data = urllib.urlopen("https://blockchain.info/charts/market-price?timespan=2years&format=json")


price_data_json = json.loads(price_data.read()) 
price_data_values=price_data_json['values']


#We run this loop first because we get prices for every dates. We make the timestamp the primary key so that when we run the second loop for all dates, which only give
#price at a 48 hour interval, it will not insert when there is already a value.
for m,  n in enumerate(price_data_values):
   
    day= n['x']
   
    day_converted=convert_time(day)
    
    price=str(round(n['y'],2))
    
    print day_converted, price
    cur.execute("INSERT INTO price (date, price) VALUES ('" + day_converted + "', '" + price + "')");
    
    conn.commit()
price_data = urllib.urlopen("https://blockchain.info/charts/market-price?timespan=all&format=json")

price_data_json = json.loads(price_data.read()) 
price_data_values=price_data_json['values']



for m,  n in enumerate(price_data_values):
    day= n['x']
    next_day=day + (24*60*60)
    day_converted=convert_time(day)
    next_day_converted=convert_time(next_day)
    price=str(round(n['y'],2))
       
        
    print day_converted, price
    print next_day_converted, price
        
   
    try:
        cur.execute("INSERT INTO price (date, price) VALUES ('" + day_converted + "', '" + price + "')");
        conn.commit()
    except:
        pass
    try:
        cur.execute("INSERT INTO price (date, price) VALUES ('" + next_day_converted + "', '" + price + "')");
        conn.commit()
    except:
        pass
            

conn.close()
