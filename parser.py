import re

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
        r'"(?P<request>.+)"',               # request "%r"
        r'(?P<status>[0-9]+)',              # status %>s
        r'(?P<size>\S+)',                   # size %b (careful, can be '-')
        r'"(?P<referer>.*)"',               # referer "%{Referer}i"
        r'"(?P<agent>.*)"',                 # user agent "%{User-agent}i"
    ]
    pattern = re.compile(r'\s+'.join(parts)+r'\s*\Z')
    # We process all
    result = []

    for file in files:
        log = open(file, 'r')
        for line in log:
            # here we match the patten against the log line
            # and them use groupdict to creat a dict object
            entry = pattern.match(line).groupdict()
            result.append(entry)
    return result
