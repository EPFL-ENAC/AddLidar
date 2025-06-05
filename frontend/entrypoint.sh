#!/usr/bin/env bash

# execute the command passed to the entrypoin
# see https://stackoverflow.com/questions/39082768/what-is-the-difference-between-cmd-and-entrypoint-in-a-dockerfile

[ "$#" -eq 0 ] && nginx -g 'daemon off;' || exec "$@"
