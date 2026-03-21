#!/bin/bash
# OnlyFounders — One-time PostgreSQL setup for WSL
# Run with: sudo bash scripts/setup-db.sh

set -e

echo "=== 1/6 Installing PostgreSQL ==="
apt-get update -qq
apt-get install -y -qq postgresql postgresql-contrib
echo "Installed: $(psql --version)"

echo "=== 2/6 Starting PostgreSQL ==="
# WSL doesn't use systemd — use pg_ctlcluster or service directly
pg_ctlcluster $(pg_lsclusters -h | head -1 | awk '{print $1, $2}') start 2>/dev/null \
  || service postgresql start 2>/dev/null \
  || pg_lsclusters

# Wait for it to be ready
for i in $(seq 1 10); do
  pg_isready -q && break
  echo "  waiting for PostgreSQL... ($i)"
  sleep 1
done
pg_isready || { echo "ERROR: PostgreSQL failed to start"; exit 1; }
echo "PostgreSQL is running"

echo "=== 3/6 Creating user 'sidda' ==="
su - postgres -c "psql -c \"CREATE USER sidda WITH SUPERUSER CREATEDB PASSWORD 'postgres';\"" 2>/dev/null \
  || echo "  User 'sidda' already exists (OK)"

echo "=== 4/6 Creating databases ==="
su - postgres -c "psql -c \"CREATE DATABASE onlyfounders OWNER sidda;\"" 2>/dev/null \
  || echo "  Database 'onlyfounders' already exists (OK)"
su - postgres -c "psql -c \"CREATE DATABASE onlyfounders_test OWNER sidda;\"" 2>/dev/null \
  || echo "  Database 'onlyfounders_test' already exists (OK)"

echo "=== 5/6 Enabling extensions ==="
su - postgres -c "psql -d onlyfounders -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'"
su - postgres -c "psql -d onlyfounders_test -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'"

echo "=== 6/6 Verifying connection ==="
su - postgres -c "psql -d onlyfounders -c 'SELECT 1 AS connected;'" && echo "Connection OK!"

echo ""
echo "=========================================="
echo "  PostgreSQL is ready!"
echo "=========================================="
echo ""
echo "Next (run as your user, not sudo):"
echo "  cd /home/sidda/OnlyFounders"
echo "  python3 -m alembic upgrade head"
echo "  pytest tests/test_marketplace.py -v"
