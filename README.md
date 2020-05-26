# endomondo-dump

## Running

Set ENV variables for USER_ID and USER_TOKEN. 

You can get these from Chrome developer tools. 
Open Endomondo, filter XHR requests, find any 'workouts' request.
It should look like this:

> https://www.endomondo.com/rest/v1/users/XXXXXX/workouts?before=2020-05-13T20%3A59%3A59.999Z&after=2020-03-26T22%3A00%3A00.000Z

XXXXX is the USER_ID

Look in the Request Headers and find the cookie. You only need USER_TOKEN from it.

## Dumping monthly listings 

Run:
> $ USER_ID=XXX USER_TOKEN=YYY python3.7 dump_monthly_listings.py

## Dumping individual workouts

Run:
> $ USER_ID=XXX USER_TOKEN=YYY python3.7 dump_individual_workouts.py


## TODO
* auto detect USER_ID
* auto detect time interval

# Charting

Optionally, you can import data to InfluxDB and chart with Grafana.

## Requirements
* influxdb python module: `pip install influxdb`

## Usage

> $ 