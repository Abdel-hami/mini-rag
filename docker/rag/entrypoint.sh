#!/bin/bash

set -e 
# run database migrations
echo "runing databse migrations..."
cd /app/models/db_schemes/minirag/
alembic upgrade head
cd /app
# start the application
echo "starting the application..."
exec "$@"

