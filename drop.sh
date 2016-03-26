#!/usr/bin/env bash

psql -c "DROP DATABASE bgame;" -U 'PashaPodolsky'
psql -c "CREATE DATABASE bgame;" -U 'PashaPodolsky'