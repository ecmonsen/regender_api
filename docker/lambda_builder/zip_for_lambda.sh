#!/bin/bash

# Zips up files needed to upload to a lambda function.

# Usage: bash zip_for_lambda.sh [-v VIRTUALENV_DIR]
#
# Then you can use this command to update the Lambda function code:

function realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

USAGE="$0 [-v VIRTUALENV_DIR] [-s SRCDIR] [-o OUTPUT_FILE] [-e EXCLUDE_FILE]"

# Defaults
THISDIR=$(realpath $(dirname $0))
SRCDIR=${THISDIR}/..
VENVDIR=$(realpath ${SRCDIR}/venv)
OUTPUT_FILE=$(realpath ${THISDIR}/function.zip)
EXCLUDE_FILE=${THISDIR}/exclude.txt

while getopts ":v:s:o:e:" opt; do
  case $opt in
    v)
      VENVDIR=$(realpath ${OPTARG})
      ;;
    s)
      SRCDIR=$(realpath ${OPTARG})
      ;;
    o)
      OUTPUT_FILE=$(realpath ${OPTARG})
      ;;
    e)
      EXCLUDE_FILE=$(realpath ${OPTARG})
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      echo "Usage: $USAGE"
      exit 1
      ;;
  esac
done

echo "Source: $SRCDIR"
echo "Venv: $VENVDIR"

set -x
echo "Deleting old output file if exists"
rm "$OUTPUT_FILE"

echo "Packaging virtual environment in $VENVDIR"

ZIPOPTS=-gqr9

# Package dependencies in virtual environment
for DIR in $(find "$VENVDIR" -name site-packages)
do
  echo "$DIR"
  cd "$DIR" && zip ${ZIPOPTS} "$OUTPUT_FILE" . --exclude ${EXCLUDE_FILE}
done

# Package our code
echo "Packaging python code"
cd "$SRCDIR" && zip ${ZIPOPTS}  "$OUTPUT_FILE" *.py *.json --exclude ${EXCLUDE_FILE}

echo "Zipfile built: ${OUTPUT_FILE}"

echo "Use this command to upload: "
echo "aws lambda update-function-code --function-name FUNCTION_NAME --zip-file fileb://$OUTPUT_FILE"