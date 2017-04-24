/*Join between GDELT and bitcoin datasets*/

SELECT
  blockchain.tx_per_day AS `num_tx`,
  GDELT.GLOBALEVENTID AS GLOBALEVENTID,
  concat(substr(cast(GDELT.SQLDATE as string),1,4),"-",substr(cast(GDELT.SQLDATE as string),5,2),"-",substr(cast(GDELT.SQLDATE as string),7,2)) AS day_timestamp,
  GDELT.Actor1Code AS Actor1Code,
  GDELT.Actor1Name AS Actor1Name,
  GDELT.Actor2Code AS Actor2Code,
  GDELT.Actor2Name AS Actor2Name,
  GDELT.AvgTone AS AvgTone,
  GDELT.SOURCEURL AS SOURCEURL
FROM
  w205_final_project.GDELT AS GDELT
INNER JOIN
  (select sum(num_tx) as tx_per_day, substr(string(timestamp),0, 10) AS bchain_TIMESTAMP
from w205_final_project.blockchain_data
group by bchain_TIMESTAMP) blockchain
ON
  blockchain.bchain_TIMESTAMP = concat(substr(cast(GDELT.SQLDATE as string),1,4),"-",substr(cast(GDELT.SQLDATE as string),5,2),"-",substr(cast(GDELT.SQLDATE as string),7,2))

/*Calculate Day Over Day Deltas*/
select current.trans as trans, current.trans-previous.previous_trans as delta, current.day_timestamp as day_timestamp

from

(SELECT * from

(select row_number() OVER(ORDER BY day_timestamp desc) as row_num, avg(num_tx) as trans, day_timestamp from w205_final_project.joined_dataset

group by day_timestamp order by day_timestamp desc) current

inner join
(select row_num-1 as previous_num, trans as previous_trans

from (
SELECT row_number() OVER(ORDER BY day_timestamp desc) as row_num, avg(num_tx) as trans, day_timestamp from w205_final_project.joined_dataset group by day_timestamp order by day_timestamp desc
)
) previous

on previous.previous_num = current.row_num)

order by delta desc

/* Top Actors and Sentiment on Increase/Decrease Days*/

select count(*) as count,avg(AvgTone) as avg_tone, Actor1Name  from w205_final_project.joined_dataset
where day_timestamp in (select day_timestamp from w205_final_project.day_over_day_deltas
where day_timestamp!='2017-03-27' and day_timestamp!='2015-09-17' and day_timestamp!='2015-09-18' and day_timestamp!='2015-07-06' and day_timestamp!='2015-09-19' and day_timestamp!='2015-07-13'
order by delta desc limit 10)
group by Actor1Name
order by count desc
limit 50

/*US and Chinese Institutions and Transaction Deltas*/
select count(*) as count,avg(AvgTone) as avg_tone, Actor1Name  from w205_final_project.joined_dataset
where day_timestamp in (select day_timestamp from w205_final_project.day_over_day_deltas
where day_timestamp!='2017-03-27' and day_timestamp!='2015-09-17' and day_timestamp!='2015-09-18' and day_timestamp!='2015-07-06' and day_timestamp!='2015-09-19' and day_timestamp!='2015-07-13'
order by delta desc limit 10)
group by Actor1Name
order by count desc
limit 50
