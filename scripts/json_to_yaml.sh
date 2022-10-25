#!/bin/bash
JSON_FILE=config.json
python3 -c 'import sys, yaml, json; print(yaml.dump(json.loads(sys.stdin.read())))' < $JSON_FILE