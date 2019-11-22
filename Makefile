VIRTUALENV=virtualenv -p python3
VENV=.
PYTHON=$(VENV)/bin/python
INSTALL_STAMP=$(VENV)/.install.stamp
APP=convertit

.IGNORE: clean
.PHONY: all install virtualenv tests

OBJECTS = $(VENV)/bin/ $(VENV)/lib/ $(VENV)/local/ $(VENV)/include/ $(VENV)/man/ .coverage d2to1-0.2.7-py2.7.egg \
	.coverage $(APP).egg-info

all: install
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON)
	$(PYTHON) setup.py develop
	touch $(INSTALL_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) $(VENV)

clean:
	rm -fr $(OBJECTS) $(DEV_STAMP) $(INSTALL_STAMP)

tests: $(INSTALL_STAMP)
	$(VENV)/bin/python setup.py test

serve: $(INSTALL_STAMP)
	$(VENV)/bin/pserve development.ini --reload
