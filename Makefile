SHELL := /bin/bash
export TEMP_FOLDER = ./tmp
# export DATASET_PATH = ./data
export DATASET_PATH = ~/dev/perso/mba_ml_in_prod/tcc/tcc-data/fashion-dataset

build:
	pip install -r requirements.txt
	# prepare data for the database (filter out corrupted records and fix the format)
	python scripts/prepare_data.py -d ${DATASET_PATH} -o $(TEMP_FOLDER)/database/data.csv
	docker-compose build

up:
	docker-compose up --detach client
	# sleep to ensure logs are there
	sleep 1
	docker-compose logs client

down:
	docker-compose down

_test:
	# add the test runners here, but don't call
	# this target directly
	docker-compose run api bin/run_tests

test: up _test down