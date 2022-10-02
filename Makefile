SHELL := /bin/bash

build:
	docker-compose build

up:
	docker-compose up --detach client
	docker-compose logs client

down:
	docker-compose down

_test:
	docker-compose run api bin/run_tests

test: up _test down