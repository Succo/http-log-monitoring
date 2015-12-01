A command line tool written for the application process of datadog.


## HTTP log monitoring console program

Create a simple console program that monitors HTTP traffic on your machine:
 * Consume an actively written-to w3c-formatted HTTP access log
 * Every 10s, display in the console the sections of the web site with the most hits (a section is defined as being what's before the second '/' in a URL. i.e. the section for "http://my.site.com/pages/create' is ""http://my.site.com/pages"), as well as interesting summary statistics on the traffic as a whole.
 * Make sure a user can keep the console app running and monitor traffic on their machine
 * Whenever total traffic for the past 2 minutes exceeds a certain number on average, add a message saying that “High traffic generated an alert - hits = {value}, triggered at {time}”
 * Whenever the total traffic drops again below that value on average for the past 2 minutes, add another message detailing when the alert recovered
 * Make sure all messages showing when alerting thresholds are crossed remain visible on the page for historical reasons.
 * Write a test for the alerting logic
 * Explain how you’d improve on this application design


## How to use it
The main program is logMonitor.py. It only require python 3.
You launch it with :

```
$.\logMonitor.py [-h] [-t threshold] (a list of log files to watch)
```

Once launched it will display different info on the log it is watching.
It display about the latest 10s:
* The most viewed section, it's number of view and the total number of view
* The most viewed query, it's number of hit and the total number of query
* The total amount of data served by the server
* The number of error served by the server

It display about the latest 2 minutes:
* the total number of view

It also display a list of all the time the number of view during the latest two minutes crossed a certain threshold (default = 1000,but anything can be passed as an argument)

If the size of the console allows it it will also display a list of all section from the latest 10s.

You can generate basic fake logs using
```
$.\logGenerator.py [-h] (a list of log files to watch)
```
You can then controls the rate at which the log is generated (number of line per seconds).
