#!/bin/sh

# Creates database role with name plato_prod and password plato.
su -l postgres -c "psql -c \"CREATE ROLE plato_prod PASSWORD 'md5557913faf8026d124385135fff478f00' NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN\""
su -l postgres -c "createdb -T template0 -O plato_prod -E utf8 plato_prod"


install -o plato -g plato -d /etc/opt/bls/plato /var/run/bls /var/log/bls/plato

