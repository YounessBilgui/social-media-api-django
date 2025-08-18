PYTHON ?= python
MANAGE = $(PYTHON) manage.py

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run:
	$(MANAGE) runserver

superuser:
	$(MANAGE) createsuperuser

seed:
	$(MANAGE) seed

test:
	$(MANAGE) test -v 2

fmt:
	$(PYTHON) -m isort .
	$(PYTHON) -m black .

lint:
	flake8 .

check:
	$(MANAGE) check

shell:
	$(MANAGE) shell

.PHONY: install migrate run superuser seed test fmt lint check shell
