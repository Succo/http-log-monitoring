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
    line += section +' HTTP/1.1" 200 '
    line += str(random.randrange(3000, 7000))
    line += ' "-" ""Mozilla/5.0 (compatible; pythonLogGenerator/0.1)""\n'
    return line

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates fake http log to a file for testing purposes')

    parser.add_argument('filenames', metavar='N', nargs='+', help='Files where to generate fake logs')
    args = parser.parse_args()
    print('writing fake http log to ' + str(args.filenames))
    print('Hit C-c to interrupt')

    while True:
        for filePath in args.filenames:
            with open(filePath, 'a') as file:
                for k in range(10):
                    file.write(lineGenerator())
                time.sleep(1)
