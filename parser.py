import re
from datetime import datetime, timezone
import threading
import time

class LogParser():
    """This class has function designed
    to process log and return a dict
    """

    def __init__(self, files, updatingDataLock):
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
        self.data["longTerm"] = {}

        # In the short term dict we will store:
        # section (a dict with a list of URL as item)
        self.data["shortTerm"]["sectionResult"] = {}
        # query (a dict with a list of the query result as item)
        self.data["shortTerm"]["queryResult"] = {}
        # total size of the content served by the server
        self.data["shortTerm"]["contentServed"] = 0

        # Keep the lock to block every time we parse data
        self.updatingDataLock = updatingDataLock

        def parseManager(parse):
            """ A function to call in loop
            display and update it
            """
            while True:
                parse()
                time.sleep(1)

        # We define a thread to call too parse the files
        self.parse = threading.Thread(target=parseManager, args= (self.parse,), daemon = True)

    def parse(self):
        """ Return a dictionnary of all
        entry stored in the list of Logs
        classed by section
        """

        self.updatingDataLock.acquire()
        # This is the time where we started processing
        # it serves to check that we are only adding recent entry to our data
        parseTime = datetime.now(timezone.utc)
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
                        section, entry = self.parseLine(line)
                        if section:
                            # We only check for the time in new file, in previously opened file, we don't wan't to miss any new line
                            if (latestLineNumber > 0) or (abs((entry["time"] - parseTime).total_seconds()) < 10):
                                # Then we add it to our dict of result to the
                                # proper place
                                if section in self.data["shortTerm"]["sectionResult"]:
                                    self.data["shortTerm"]["sectionResult"][section] += [entry]
                                else:
                                    self.data["shortTerm"]["sectionResult"][section] = [entry]
                    lineNumber += 1
                self.files[numberOfFileRead] = (file,lineNumber-1)
        self.updatingDataLock.release()
        return

    def parseLine(self, line):
        # here we match the patten against the log line
        # and them use groupdict to creat a dict object
        matched = self.pattern.match(line)
        # In case of broken entry to avoid having the program plant
        if (matched == None):
            return (False , False)
        entry = matched.groupdict()
        date = entry["time"]
        # we take the date a python date object for easier manipulation
        entry["time"] = datetime.strptime(date, "%d/%b/%Y:%H:%M:%S %z")
        # we process the request to remove first the queries,
        # then extract the section
        section = self.clearQuery(entry["ressource"])
        section = self.extractSection(section)
        return (section, entry)

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
        for query in requestAndQuery[1:]:
            # We are going to stock the query in an array
            # to be able to generate other interesting stats
            key, sep, value = query.partition("=")
            if key in self.data["shortTerm"]["queryResult"]:
                self.data["shortTerm"]["queryResult"][key] += [value]
            else:
                self.data["shortTerm"]["queryResult"][key] = [value]
        # We then return the request striped of query
        return requestAndQuery[0]
