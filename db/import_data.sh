#!/bin/bash

set -e

# pg_restore --create -h "/var/run/postgresql/" --no-password --username="postgres" --role="postgres" --dbname="aip" --jobs="1" --verbose ../initialization/testtest.bak

psql -U "postgres" -h "/var/run/postgresql/" --no-password -d "aip" < ../initialization/data.backup


