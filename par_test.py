# pool.py
from multiprocessing import Pool
import time
import multiprocessing
from datetime import datetime
from datetime import timedelta, date, datetime
startTime = datetime.now()


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

cores_to_use=multiprocessing.cpu_count() - 1
print cores_to_use
def take_nap(x):
    #time.sleep(x)
    print "ahh...refreshing. It's %s!" % time.time()

p = Pool(5)

#p.map(take_nap, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])

start_date = date(1900, 1, 27)
end_date = date(2200, 1, 28)
    
    
for single_date in daterange(start_date, end_date):
    print single_date

print datetime.now() - startTime
