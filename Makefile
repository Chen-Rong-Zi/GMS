.PHONY: test dep always_run

SHELL := /bin/bash
PY := ${Project}/.venv/bin/python3

ifeq (${Project},)
 $(error 找不到Project 这个变量)
endif

# if want to interpret a script, using `make script-name.gms`

always_run:

dep: requirements.txt
	${PY} -m pip install -r requirements.txt

test: always_run
	@pytest

run: always_run
	@cd ../ && ${PY} -m GMS.interpretor
	
%.gms: always_run
	@cd ../ && ${PY} -m GMS.interpretor $(shell realpath $@)
