#!/bin/bash

##clear out the database in case of re-runs
psql -U postgres -d blockchain -c "DELETE FROM blocks"



for i in {2009..2017}
do
 echo "Year: $i"
 nohup python2.7 -u query_blockchain.py $i > logfile_$i.txt &
 #echo $job
 #wait $job || let "FAIL+=1"
done
wait 
echo "your custom done"

##Proof that the timestamp works
psql -U postgres -d blockchain -c "Select extract(year from timestamp), count(*)  from blocks group by extract(year from timestamp);"



