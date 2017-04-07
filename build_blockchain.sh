#!/bin/bash
start=`date +%s`
##clear out the database in case of re-runs
psql -U postgres -d blockchain -c "DELETE FROM blocks"
psql -U postgres -d blockchain -c "DELETE FROM price"


for i in {2009..2017}
do
 echo "Year: $i"
 nohup python2.7 -u query_blockchain.py $i > logfile_$i.txt &
 #echo $job
 #wait $job || let "FAIL+=1"
done
wait 
echo "Now we are going to add in the heights that somehow were missing"

nohup python2.7 -u add_in_missing_heights.py > adding_in_missing_heights &

wait

end=`date +%s`
runtime=$((end-start))
echo $runtime
echo "That is seconds. All done"



##Proof that the timestamp works and height plus max check
psql -U postgres -d blockchain -c "Select extract(year from timestamp), count(*)  from blocks group by extract(year from timestamp);"

echo "This is the number occurrences of block height"
psql -U postgres -d blockchain -c "Select count(height)  from blocks;"

echo "This is the max block height"
psql -U postgres -d blockchain -c "Select count(height)  from blocks;"

python2.7 get_price.py 







