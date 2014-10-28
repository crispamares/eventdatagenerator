# Event Data Generator

This proyect is a simple script that generates event datasets in the
EventFlow file format.

It also has a simple web interface thar is prepared to run in Google
AppEngine.

## Script Usage

The online help describes all accepted params: 

```
$ python datagen.py  -h
usage: datagen.py [-h] [-e NUM_OF_EVENTS | -n NUM_OF_NODES]
                  [--years NUM_OF_YEARS] [--stddev STDDEV] [--repeat COPIES]
                  [--only_points]
                  R

Generate EventFlow datasets.

positional arguments:
  R                     the number of records in the dataset

optional arguments:
  -h, --help            show this help message and exit
  -e NUM_OF_EVENTS, --num_of_events NUM_OF_EVENTS
                        Desired number of events per record in the dataset
  -n NUM_OF_NODES, --num_of_nodes NUM_OF_NODES
                        Desired number of nodes per record in the dataset
  --years NUM_OF_YEARS  the total of years of records
  --stddev STDDEV       Standard deviation affects random elections such as
                        time shifts
  --repeat COPIES       The numbers of copies of generated records to ensure
                        aggregation in EventFlow
  --only_points         Generate dataset with only point events (A.K.A.
                        Milestones)

```

In the next example we are generating a dataset of 5 records each one
with 4 events:

```
$ python datagen.py  -e 4 5
0	Admitted	10/28/2012
0	Stroke	04/29/2013
0	Drug A	10/28/2013	04/29/2014
0	Drug B	04/29/2013	10/28/2013
1	Stroke	04/29/2014
1	Diagnosed	10/28/2013
1	Diagnosed	10/28/2012
1	Drug A	10/28/2012	04/29/2013
2	Diagnosed	10/28/2013
2	Admitted	04/29/2014
2	Admitted	04/29/2013
2	Drug B	04/29/2012	10/28/2012
3	Drug A	04/29/2013	10/28/2013
3	Drug A	04/29/2012	10/28/2012
3	Admitted	04/29/2014
3	Diagnosed	04/29/2013
4	Stroke	10/28/2013
4	Stroke	10/28/2012
4	Diagnosed	04/29/2014
4	Diagnosed	04/29/2013

```

## Web interface

The web interface is very simple. Uses webapp for the server side code
and angular for the client ui code.

The only requisite is the [Google App Engine SDK|https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python]

If you want to run the app in your machine type after unzipping the sdk: 

```
$ python dev_appserver.py eventdatagenerator/
```
