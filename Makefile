###############################################
#
# Nelp plugin for custom development commands.
#
###############################################

intl_imports = ./node_modules/.bin/intl-imports.js
OPENEDX_ATLAS_PULL=true
ATLAS_OPTIONS=--repository=nelc/futurex-translations --revision=open-release/redwood.master

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
	$(TOX) pylint ./eox_nelp --rcfile=./setup.cfg --fail-on=I0021
	$(TOX) isort --check-only --diff ./eox_nelp

python-test: clean install-test-reqs## Run test suite.
	$(TOX) coverage run --source ./eox_nelp manage.py test
	$(TOX) coverage report -m --fail-under=93

complexity: clean install-test-reqs## Run complexity suite with flake8.
	$(TOX) flake8  --max-complexity 10 eox_nelp

run-tests: python-test quality complexity## run all tests

automation-run-tests: install-automation-reqs run-tests ## run all tests with tox

build_react_apps: pull_react_translations
	npm run build
	git checkout -- eox_nelp/i18n/index.js

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

pull_react_translations:
	rm -rf src/i18n/messages
	mkdir -p src/i18n/messages
	cd src/i18n/messages \
	  && export PATH="$(shell pwd)/node_modules/.bin:$$PATH" && atlas pull $(ATLAS_OPTIONS) \
	           translations/frontend-platform/src/i18n/messages:frontend-platform \
	           translations/paragon/src/i18n/messages:paragon \
	           translations/frontend-essentials/src/i18n/messages:frontend-essentials

	$(intl_imports) frontend-platform paragon frontend-essentials
	cp -r src/i18n/* eox_nelp/i18n/
	rm -rf src

# Variables for documentation
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXSOURCE  = docs/source
SPHINXBUILD_DIR = docs/build

.PHONY: help clean docs docs-html docs-dirhtml docs-singlehtml docs-pickle docs-json docs-htmlhelp docs-qthelp docs-devhelp docs-epub docs-latex docs-man docs-texinfo docs-text docs-changes docs-linkcheck docs-doctest docs-coverage docs-xml docs-pseudoxml docs-dummy install-docs-reqs docs-api

install-docs-reqs: ## install documentation requirements
	pip install -r requirements/docs.txt

docs-api: install-docs-reqs ## Generate API documentation
	python $(SPHINXSOURCE)/api/autodoc.py

# Documentation targets
docs-help:
	@$(SPHINXBUILD) -M help "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)" $(SPHINXOPTS) $(O)

docs: install-docs-reqs docs-api docs-html  ## Build documentation in HTML format (installs requirements first)

docs-html: ## Build documentation in HTML format
	$(SPHINXBUILD) -b html "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/html" $(SPHINXOPTS)
	@echo
	@echo "Build finished. The HTML pages are in $(SPHINXBUILD_DIR)/html."

docs-dirhtml:
	$(SPHINXBUILD) -b dirhtml "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/dirhtml" $(SPHINXOPTS)

docs-singlehtml:
	$(SPHINXBUILD) -b singlehtml "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/singlehtml" $(SPHINXOPTS)

docs-pickle:
	$(SPHINXBUILD) -b pickle "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/pickle" $(SPHINXOPTS)

docs-json:
	$(SPHINXBUILD) -b json "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/json" $(SPHINXOPTS)

docs-htmlhelp:
	$(SPHINXBUILD) -b htmlhelp "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/htmlhelp" $(SPHINXOPTS)

docs-qthelp:
	$(SPHINXBUILD) -b qthelp "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/qthelp" $(SPHINXOPTS)

docs-devhelp:
	$(SPHINXBUILD) -b devhelp "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/devhelp" $(SPHINXOPTS)

docs-epub:
	$(SPHINXBUILD) -b epub "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/epub" $(SPHINXOPTS)

docs-latex:
	$(SPHINXBUILD) -b latex "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/latex" $(SPHINXOPTS)

docs-man:
	$(SPHINXBUILD) -b man "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/man" $(SPHINXOPTS)

docs-texinfo:
	$(SPHINXBUILD) -b texinfo "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/texinfo" $(SPHINXOPTS)

docs-text:
	$(SPHINXBUILD) -b text "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/text" $(SPHINXOPTS)

docs-changes:
	$(SPHINXBUILD) -b changes "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/changes" $(SPHINXOPTS)

docs-linkcheck:
	$(SPHINXBUILD) -b linkcheck "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/linkcheck" $(SPHINXOPTS)

docs-doctest:
	$(SPHINXBUILD) -b doctest "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/doctest" $(SPHINXOPTS)

docs-coverage:
	$(SPHINXBUILD) -b coverage "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/coverage" $(SPHINXOPTS)

docs-xml:
	$(SPHINXBUILD) -b xml "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/xml" $(SPHINXOPTS)

docs-pseudoxml:
	$(SPHINXBUILD) -b pseudoxml "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/pseudoxml" $(SPHINXOPTS)

docs-dummy:
	$(SPHINXBUILD) -b dummy "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)/dummy" $(SPHINXOPTS)

docs-clean:  ## Clean documentation build directory
	rm -rf $(SPHINXBUILD_DIR)/*

# Add docs-clean to the clean target if it exists
clean: docs-clean

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
docs-%: Makefile
	@$(SPHINXBUILD) -M $* "$(SPHINXSOURCE)" "$(SPHINXBUILD_DIR)" $(SPHINXOPTS) $(O)
