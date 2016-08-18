#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="${SCRIPT_DIR}/service.pid"

rm ${SCRIPT_DIR}/*.log.*
kill -TERM `cat ${PID_FILE}`
rm ${PID_FILE}
