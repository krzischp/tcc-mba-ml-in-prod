SHELL := /bin/bash

build:
	docker-compose build

up:
	docker-compose up --detach client
	docker-compose logs client

down:
	docker-compose down
