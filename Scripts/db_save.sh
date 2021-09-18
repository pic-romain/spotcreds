#!/bin/bash
mongodump --db=dbspotcred --out="/home/db_save/$(date +"%Y_%m_%d")"
