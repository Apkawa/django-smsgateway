# $Header: /var/cvsroot/SMPPSim2/startsmppsim.sh,v 1.6 2005/12/09 17:35:32 martin Exp $
#! /bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="${SCRIPT_DIR}/service.pid"

java -Djava.net.preferIPv4Stack=true \
     -Djava.util.logging.config.file=conf/logging.properties \
     -jar ${SCRIPT_DIR}/smppsim.jar ${SCRIPT_DIR}/conf/smppsim.props &
echo "$!" > ${PID_FILE}
