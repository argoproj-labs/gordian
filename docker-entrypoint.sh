#!/bin/sh
set -e

# this if will check if the first argument is a flag
if [ "$#" -eq 0 ] || [ "${1#-}" != "$1" ]; then
    set -- gordian "$@"
fi

# check for the expected command
if [ "$1" = 'gordian' ]; then
    exec gordian "$@"
fi

# else default to run whatever the user wanted like "bash" or "sh"
exec "$@"
