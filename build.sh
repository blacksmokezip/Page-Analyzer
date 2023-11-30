#!/usr/bin/env bash
export $(xargs <.env)
make install && psql -a -d $DATABASE_URL -f database.sql