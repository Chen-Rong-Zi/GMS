.PHONY: test dep always_run

SHELL := /bin/bash
PY := ${Project}/.venv/bin/python3

ifeq (${Project},)
 $(error 找不到Project 这个变量)
endif

ifeq (${VIRTUAL_ENV},)
 $(error 需要python virtual env环境, 尝试source .venv/bin/activate)
endif

# if want to interpret a script, using `make script-name.gms`

alwaygs_run:

clean:
	@rm -rf $(shell find . -iname '__pycache__')

dep: requirements.txt
	${PY} -m pip install -r requirements.txt

test:
	@pytest

fuzzy-test:
	@for i in $(shell find . -iname '*.gms');do\
		${PY} interpretor.py -p $$i & \
	done; \
	wait;

run:
	@${PY} interpretor.py
	
debug:
	@viztracer ${PY} interpretor.py

%.gms: always_run
	${PY} interpretor.py $(shell realpath $@)
