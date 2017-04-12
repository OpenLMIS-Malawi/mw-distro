# Usage:
# First argument - username
# Second argument - database host
# Third argument - database port

COMMAND="UPDATE auth.oauth_client_details SET resourceids = resourceids || ',reports' where (clientid = 'trusted-client' or clientid = 'user-client')";
DATABASE_NAME="open_lmis";

psql -U "$1" -h "$2" -p "$3" -d "$DATABASE_NAME" -W -t -c "$COMMAND"

