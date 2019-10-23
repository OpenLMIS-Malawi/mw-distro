#!/bin/bash

set -x

updateProperty() {
  grep -q "^${1}" ${3} && sed -i "s|^${1}=.*$|${1}=${2}|" ${3} || echo "${1}=${2}" >> ${3}
}

createOpenLmisProperties() {
  FILE="./conf/openlmis.properties"

  if [ ! -f ${FILE} ];
  then
    touch ${FILE}
  fi

  updateProperty "openlmis.baseUrl" "${OL_BASE_URL}" "${FILE}"
  updateProperty "openlmis.trustedHostname" "${TRUSTED_HOSTNAME}" "${FILE}"

  updateProperty "openlmis.admin.username" "${OL_ADMIN_USERNAME}" "${FILE}"
  updateProperty "openlmis.admin.password" "${OL_ADMIN_PASSWORD}" "${FILE}"

  updateProperty "openlmis.authServer.clientId" "${AUTH_SERVER_CLIENT_ID}" "${FILE}"
  updateProperty "openlmis.authServer.clientSecret" "${AUTH_SERVER_CLIENT_SECRET}" "${FILE}"

  updateProperty "openlmis.fhir.id" "${FHIR_ID}" "${FILE}"
  updateProperty "openlmis.fhir.password" "${FHIR_PASSWORD}" "${FILE}"

  updateProperty "openlmis.postgres.password" "${POSTGRES_PASSWORD}" "${FILE}"
}

${NIFI_HOME}/bin/nifi.sh stop &&
cp /config/nifi/libs/* lib/ &&
cp /config/nifi/conf/* conf &&
createOpenLmisProperties &&
/config/nifi/scripts/download-toolkit.sh $1 &&
/config/nifi/scripts/preload.sh init $1 &&
cd /opt/nifi/nifi-$1 &&
../scripts/start.sh
