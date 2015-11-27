import argparse
import time
import random
from datetime import datetime, timezone

def lineGenerator():
    """ Function to generate fake line similar to http log
    For now only time andsection are important to addapt
    """
    # List of random section to pick from
    sectionList = [
        '/js',
        '/img',
        '/css',
        '/',
        '/videos',
        '/http-bind',
        '/skins',
        '/plugins',
        '/piwik',
        '/program',
        '/users',
        '/directs',
        '/load.php',
        '/favicon.ico',
        '/index.php',
        '/fonticons',
        '/robots.txt',
        '/categories',
        '/pages',
        '/resources',
        '/images',
        '/nxmen'
    ]
    line =  "127.0.0.1 - - ["
    date = datetime.now(timezone.utc).strftime("%d/%b/%Y:%H:%M:%S %z")
    line += date +'] "GET '
    section = sectionList[random.randrange(21)]
    line += section +' HTTP/1.1" 200 - "-" ""Mozilla/5.0 (compatible; pythonLogGenerator/0.1)""\n'
    return line

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('filename')
    args = parser.parse_args()
    print('writing fake http log to ' + args.filename)
    print('Hit C-c to interrupt')

    while True:
        with open(args.filename, 'a') as file:
            file.write(lineGenerator())
        time.sleep(1)
