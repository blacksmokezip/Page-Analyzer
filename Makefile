install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run --port 8000

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

lint:
	poetry run flake8 page_analyzer