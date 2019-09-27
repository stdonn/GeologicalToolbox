#!/bin/bash

if [[ $# -lt 1 ]]; then
	echo "a script description is necessary..."
	exit 1
fi

DB_PATH=/tmp/
while [[ -e $DB_PATH ]]; do
	DB_PATH="/tmp/$(uuidgen).sqlite"
done

echo "temporary database: $DB_PATH"
export PYTHONPATH=`pwd`/../

alembic -x db_url=sqlite:///$DB_PATH upgrade head
alembic -x db_url=sqlite:///$DB_PATH revision --autogenerate -m $1

rm $DB_PATH
