import re
from datetime import datetime, timezone

class LogParser():
    """This class has function designed
    to process log and return a dict
    """

    def __init__(self, files):
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
        self.files = files
        # a dict to save list value associed to a key in query made to the server
        self.queryResult = {}

    def parse(self):
        """ Return a dictionnary of all
        entry stored in the list of Logs
        classed by section
        """
        result = {}
        for file in self.files:
            with open(file, 'r') as log:
                for line in log:
                    # here we match the patten against the log line
                    # and them use groupdict to creat a dict object
                    matched = self.pattern.match(line)
                    # In case of broken entry to avoid breaking the program
                    if (matched == None):
                        break
                    entry = matched.groupdict()
                    date = entry["time"]
                    # we take the date a python date object for easier manipulation
                    entry["time"] = datetime.strptime(date, "%d/%b/%Y:%H:%M:%S %z")
                    #print((entry["time"] - datetime.now(timezone.utc)).total_seconds())
                    # we process the request to remove first the queries,
                    # then extract the section
                    section = self.clearQuery(entry["ressource"])
                    section = self.extractSection(section)
                    if section in result:
                        result[section] += [entry]
                    else:
                        result[section] = [entry]
        return result

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
            if key in self.queryResult:
                self.queryResult[key] += [value]
            else:
                self.queryResult[key] = [value]
        # We then return the request striped of query
        return requestAndQuery[0]
