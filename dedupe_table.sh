#! /bin/bash

# usage: ./dedupe_table.sh <dataset name> <source table> <dest table>

replace=""

if [ $2=$3 ];
then
replace="--replace"
fi

bq query $replace --destination_table=$1.$3 "SELECT *
FROM (
  SELECT
      *,
      ROW_NUMBER()
          OVER (PARTITION BY hashvalue)
          row_number
  FROM $1.$2
)
WHERE row_number = 1"
