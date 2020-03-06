help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "lint - check style with flake8"
	@echo "release - package and upload a release"
	@echo "install - install the package in the current virtual environment (or global default environment)"
	@echo "full-install - install the package in a fresh virtual environment"

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
	flake8 python-lambda tests

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

install: clean
	python setup.py install

full-install: clean
	virtualenv --python python3.6 torb_env
	source torb_env/bin/activate && pip install --upgrade pip
	source torb_env/bin/activate && python setup.py install
