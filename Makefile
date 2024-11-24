.PHONY: test dep

SHELL := /bin/bash
PY := ${Project}/.venv/bin/python3

ifeq (${Project},)
 $(error 找不到Project 这个变量)
endif


dep: requirements.txt
	${PY} -m pip install -r requirements.txt

test:
	@pytest

run:
	@cd ../ && ${PY} -m GMS.interpretor
