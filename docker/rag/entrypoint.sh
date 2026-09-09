#!/bin/bash

set -e 

echo "runing databse migrations..."
cd /app/models/db_schemes/minirag
alembic upgrade head
cd /app