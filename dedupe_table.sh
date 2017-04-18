#! /bin/bash

# usage: ./dedupe_table.sh <dataset name> <source table> <dest table>

bq query --destination_table=$1.$3 "SELECT *
FROM (
  SELECT
      *,
      ROW_NUMBER()
          OVER (PARTITION BY hashvalue)
          row_number
  FROM $1.$2
)
WHERE row_number = 1"