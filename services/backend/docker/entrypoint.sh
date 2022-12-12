#!/bin/bash

/wait-for-postgres.sh db:5432 --timeout=0
exec "$@"