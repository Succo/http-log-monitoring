import re
import time

def parse(files):
    """This create a list with the log entry
    It take in argument a list of log files
    Each entry is a dict
    """

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
    pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
    # We process all
    result = []

    for file in files:
        with open(file, 'r') as log:
            for line in log:
                # here we match the patten against the log line
                # and them use groupdict to creat a dict object
                entry = pattern.match(line).groupdict()
                date = entry["time"]
                # we take the date a python date object for easier manipulation
                entry["time"] = time.strptime(date, "%d/%b/%Y:%H:%M:%S %z")
                print(extractSection(entry["ressource"]))
                result.append(entry)
    return result

def extractSection(ressource):
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
