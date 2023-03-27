###############################################
#
# Nelp plugin for custom development commands.
#
###############################################

# Define PIP_COMPILE_OPTS=-v to get more information during make upgrade.
PIP_COMPILE = pip-compile --rebuild --upgrade $(PIP_COMPILE_OPTS)

.DEFAULT_GOAL := help

ifdef TOXENV
TOX := tox -- #to isolate each tox environment if TOXENV is defined
endif

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: ## delete most git-ignored files
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	rm -fr *.egg-info

clean-coverage: clean ##clean and clean coverage file
	coverage erase

requirements: ## install environment requirements
	pip install -r requirements/base.txt

install-automation-reqs: ## install tox requirements
	pip install -r requirements/tox.txt

install-test-reqs: ## install test requirements
	$(TOX) pip install -r requirements/test.txt --exists-action w

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -qr requirements/pip-tools.txt
	# Make sure to compile files after any other files they include!
	$(PIP_COMPILE) -o requirements/pip-tools.txt requirements/pip-tools.in
	$(PIP_COMPILE) -o requirements/base.txt requirements/base.in
	$(PIP_COMPILE) -o requirements/test.txt requirements/test.in
	$(PIP_COMPILE) -o requirements/tox.txt requirements/tox.in

	grep -e "^django==" requirements/test.txt > requirements/django.txt

quality: clean install-test-reqs## check coding style with pycodestyle and pylint
	$(TOX) pycodestyle ./eox_nelp
	$(TOX) pylint ./eox_nelp --rcfile=./setup.cfg
	$(TOX) isort --check-only --diff ./eox_nelp

python-test: clean install-test-reqs## Run test suite.
	$(TOX) coverage run --source ./eox_nelp manage.py test
	$(TOX) coverage report -m --fail-under=90

complexity: clean install-test-reqs## Run complexity suite with flake8.
	$(TOX) flake8  --max-complexity 10 eox_nelp

run-tests: python-test quality complexity## run all tests

automation-run-tests: install-automation-reqs run-tests ## run all tests with tox

##-----------------------------Translations section-------------------------
extract-translations: ## extract strings to be translated, outputting .mo files
	./manage.py makemessages -l ar   -i manage -i setup -i "venv/*"

compile-translations: ## compile translation files, outputting .po files for each supported language
	cd eox_nelp && ../manage.py compilemessages

detect-changed-source-translations:
	cd eox_nelp && i18n_tool changed

pull-translations: ## pull translations from Transifex
	tx pull -af --mode reviewed

push-translations: ## push source translation files (.po) from Transifex
	tx push -s
