#! /usr/bin/env python3

"""mymath - our example math module"""

from optparse import OptionParser

pi = 3.14159

def area(r):
    """area(r): return the area of a circle with radius r."""
    global pi
    return(pi * r * r)

def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-x", "--xray", dest="xray",
                      help="specify xray strength factor")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    print("options:", str(options))
    print("arguments:", args)
    
main()
