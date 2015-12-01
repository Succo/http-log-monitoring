import re
from datetime import datetime, timezone
import threading
import time

class LogParser():
    """This class has function designed
    to process log and return a dict
    """

    def __init__(self, files, updatingDataLock, threshold):
        self.THRESHOLDS = threshold
        # This list of regex is used to parse each line
        # Most entry are defined as text between space
        parts = [
            r'(?P<host>\S+)',                   # host %h
            r'\S+',                             # indent %l (unused)
            r'(?P<user>\S+)',                   # user %u
            r'\[(?P<time>.+)\]',                # time %t
            r'"(?P<method>.+)',                 # method
            r'(?P<ressource>\S+)',              # ressource
            r'(?P<protocol>\S+)"',              # protocol
            r'(?P<status>[0-9]+)',              # status %>s
            r'(?P<size>\S+)',                   # size %b (careful, can be '-')
            r'"(?P<referer>.*)"',               # referer "%{Referer}i"
            r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
        ]
        self.pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
        #This is the list of files to scan for logs
        self.files = []
        for file in files:
            # We fill it with tuple containing file, and number of line read on file
            # It will help to find the latest logs faster
            self.files += [(file, 0)]

        # A dict to save data parsed from the log
        self.data = {}

        # Long (2 min) and short (10 s) term data
        self.data["shortTerm"] = {}
        # Long term will be used as a pile of 12 item (2min / 10s = 12)
        self.data["longTerm"] = []

        # alert will be a list of all the times where the thresholds is crossed
        self.data["alert"] = []

        # In the short term dict we will store:
        # section (a dict with a list of URL as item)
        self.data["shortTerm"]["sectionResult"] = {}
        # query (a dict with a list of the query result as item)
        self.data["shortTerm"]["queryResult"] = {}
        # total size of the content served by the server
        self.data["shortTerm"]["contentServed"] = 0
        # total size of the content served by the server
        self.data["shortTerm"]["failedRequest"] = 0

        # Keep the lock to block every time we parse data
        self.updatingDataLock = updatingDataLock

        def parseManager():
            """ A function to call in loop
            display and update it
            """
            while True:
                self.updateData()
                self.parse()
                time.sleep(10)

        # We define a thread to call too parse the files
        self.parserManager = threading.Thread(target=parseManager, daemon = True)

    def parse(self):
        """ Return a dictionnary of all
        entry stored in the list of Logs
        classed by section
        """

        self.updatingDataLock.acquire()
        # This is the time where we started processing
        # it serves to check that we are only adding recent entry to our data
        parseTime = datetime.now(timezone.utc)
        shortTerm = self.data["shortTerm"]
        for numberOfFileRead  in range(len(self.files)):
            # we read the list that way to be able to update it place
            file, latestLineNumber = self.files[numberOfFileRead]
            with open(file, 'r') as log:
                # This is the number of line read in the file
                # It is compared to the biggest line
                # read on previous read
                lineNumber = 0
                # We are on an already opened file
                # Latest line number correspond to the oldest line of the previous read
                for line in log:
                    if (lineNumber >= latestLineNumber):
                        # first unread line of the file since last call
                        # We process it
                        section, entry, queryList= self.parseLine(line)
                        if section:
                            # We only check for the time in new file, in previously opened file, we don't wan't to miss any new line
                            if (latestLineNumber > 0) or (abs((entry["time"] - parseTime).total_seconds()) < 10):
                                # Then we add it to our dict of result to the
                                # proper place
                                if section in shortTerm["sectionResult"]:
                                    shortTerm["sectionResult"][section] += 1
                                else:
                                    shortTerm["sectionResult"][section] = 1
                                if (entry["size"] != "-"):
                                    shortTerm["contentServed"] += int(entry["size"])
                                if (entry["status"] != "-") and (int(entry["status"]) > 400) and (int(entry["status"]) < 500):
                                    shortTerm["failedRequest"] += 1
                                for query in queryList:
                                    if query in self.data["shortTerm"]["queryResult"]:
                                        shortTerm["queryResult"][query] += 1
                                    else:
                                        shortTerm["queryResult"][query] = 1
                    lineNumber += 1
                self.files[numberOfFileRead] = (file,lineNumber)
        self.updatingDataLock.release()
        return

    def parseLine(self, line):
        # here we match the patten against the log line
        # and them use groupdict to creat a dict object
        matched = self.pattern.match(line)
        # In case of broken entry to avoid having the program plant
        if (matched == None):
            return (False , False, False)
        entry = matched.groupdict()
        date = entry["time"]
        # we take the date a python date object for easier manipulation
        entry["time"] = datetime.strptime(date, "%d/%b/%Y:%H:%M:%S %z")
        # we process the request to remove first the queries,
        # then extract the section
        section, queryList= self.clearQuery(entry["ressource"])
        section = self.extractSection(section)
        return (section, entry, queryList)

    def extractSection(self, ressource):
        """Given a string corresponding to a
        requested ressource will return
        the section
        """
        indexOfLastBackSlash = ressource.rfind("/")
        if (indexOfLastBackSlash == 0):
            # Only one / in given entry
            return ressource
        elif (indexOfLastBackSlash > 0):
            # We need to return the first parts
            return ressource[:ressource.index("/",1)]
        elif (indexOfLastBackSlash < 0):
            raise ValueError('Badly Formatted ressource string')

    def clearQuery(self, ressource):
        """Remove all query parameter from a request,
        return both an array of the query parameter
        and the request itself
        """
        # we split the string to get an array of the querry
        # and the reqest itself
        requestAndQuery = re.split(r'[&?;]', ressource )
        def removeValue(query):
            """ A function to remove to keep only
            the key from a query string
            """
            key, sep, value = query.partition("=")
            return key
        queryList = map(removeValue, requestAndQuery[1:])
        # We then return the request striped of query and a list of the query made
        return (requestAndQuery[0], queryList)

    def updateData(self):
        """Will serves to update the data obect
        It will update the long term part (clearing old entry...)
        """
        # In the long term dict we just keep the number of request in the last segment
        numberOfRequest = 0
        for section in self.data["shortTerm"]["sectionResult"]:
            numberOfRequest += self.data["shortTerm"]["sectionResult"][section]
        # We only keep up to 12 item if the long term result
        if (len(self.data["longTerm"])) > 11:
            self.data["longTerm"].pop(0)

        self.data["longTerm"].append(numberOfRequest)

        # if the alert stack is empty or is finished by an alert below thresholds
        if ((len(self.data["alert"]) == 0) or (self.data["alert"][len(self.data["alert"])-1][0] < self.THRESHOLDS)):
            if (sum(self.data["longTerm"]) > self.THRESHOLDS):
                # We add a tuple, the first item is the number of hit
                self.data["alert"].append((sum(self.data["longTerm"]), datetime.now()))
        else:
            # we are already above thresholds so we nedd to check when we cross the other way
            if (sum(self.data["longTerm"]) < self.THRESHOLDS):
                # We add a tuple, the first item is the number of hit
                self.data["alert"].append((sum(self.data["longTerm"]), datetime.now()))

        # In the short term dict we will store:
        # section (a dict with a list of URL as item)
        self.data["shortTerm"]["sectionResult"] = {}
        # query (a dict with a list of the query result as item)
        self.data["shortTerm"]["queryResult"] = {}
        # total size of the content served by the server
        self.data["shortTerm"]["contentServed"] = 0
        # total size of the content served by the server
        self.data["shortTerm"]["failedRequest"] = 0
