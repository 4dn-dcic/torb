help:
	@make info


clean: clean-build clean-pyc clean-merge clean-env

clean-build: clean-env
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: clean-env
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-merge: clean-env
	find . -name '*.orig' -exec rm -f {} +

clean-env:
	rm -rf *env/

lint:
	flake8 torb tests

release: clean
	poetry publish

build:
	poetry install

install: clean
	poetry install

full-install: clean
	virtualenv --python python3.6 torb_env
	source torb_env/bin/activate && poetry install

torb_env:
	if [ ! -e torb_env ]; then virtualenv --python python3.6 torb_env; fi

test: torb_env
	source torb_env/bin/activate && echo "Disabled for now: Mocks out of date. Fix before reenabling." && exit 1 # pytest

info:
	@: $(info Here are some suggestions:)
	@echo "- Use 'make clean' to remove all build, test, coverage and Python artifacts."
	@echo "- Use 'make lint' to check style with flake8."
	@echo "- Use 'make release' to package and upload a release."
	@echo "- Use 'make install' to install the package in the current virtual environment (or global default environment)."
	@echo "- Use 'make full-install' to install the package in a fresh virtual environment."
	@echo "- Use 'make test' to run tests."
