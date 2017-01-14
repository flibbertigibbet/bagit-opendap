#Process

## Description

OPeNDAP server at https://opendap.co-ops.nos.noaa.gov hosts the data used by https://tidesandcurrents.noaa.gov/

## Structure

There are eleven dataset endpoints, one of which is `allDatasets`, which appears to just be a little metadata for the other ten datasets. The ten dataset endpoints have either three or four required query parameters:

 - station ID
 - start date
 - end date
 - datum (not used by all IOOS_Wind, IOOS_Water_Temperature, IOOS_Conductivity, IOOS_Barometric_Pressure, or IOOS_Air_Temperature)

 A maximum of 31 days may be queried at a time.

 ## The Plan

Query as JSON each month in the available data range (what is the available data range?) for each available station and datum.

## Stations

The front-end site queries for the list of all stations here: https://tidesandcurrents.noaa.gov/cgi-bin/stationbarsearch.cgi?&term=&type=active

The responses contain just a `name` field that appears to be the station ID concatenated with the description.

109 months for air temp for 365 usable stations. ~800KB each, so ~30GB for that dataset.
30 GB * 5 non-datum datasets +
30 GB * 5 dataum datasets * 9 datums

So rough estimate of ~1.5 terabytes for full database.
