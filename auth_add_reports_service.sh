# Usage:
# First argument - database connection
# Second argument - username

COMMAND="UPDATE auth.oauth_client_details SET resourceids = 'auth,example,requisition,notification,referencedata,fulfillment,stockmanagement,reports' where clientid = 'trusted-client'";

psql "$1" -U "$2" -t -c "$3"
