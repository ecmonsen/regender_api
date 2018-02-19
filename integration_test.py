import argparse
import sys
import json
import logging


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.error("What")

parser = argparse.ArgumentParser()
parser.add_argument("handler_name", help="Handler to test", choices=["go", "start"])
parser.add_argument("-f", "--file", help="File containing body of input. If omitted, stdin will be used")

args = parser.parse_args()

if args.file:
    with open(args.file, "r") as f:
        event = json.load(f)
else:
    event = json.load(sys.stdin)

import handler
if args.handler_name == "go":
    response = handler.regender_go(event, None)
else:
    response = handler.regender_start(event, None)


print json.dumps(response, indent=2)