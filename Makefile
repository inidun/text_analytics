
include .env

.DEFAULT_GOAL=lint

SOURCE_FOLDERS=notebooks scripts src tests

install_dev: models install_lab
	@echo "Install dev dependencies"

models: spacy_download nltk_download

spacy_download:
	@poetry run python -m spacy download en_core_web_sm

nltk_download:
	@poetry run python -c "import nltk; nltk.download('stopwords')"
	@poetry run python -c "import nltk; nltk.download('punkt')"

install_lab:
	@poetry run jupyter labextension install \
    	@jupyter-widgets/jupyterlab-manager \
    	@bokeh/jupyter_bokeh \
    	jupyter-matplotlib \
# init:
# 	@pip install --upgrade pip
# ifeq (, $(PIPENV_PATH))
# 	@pip install poetry --upgrade
# endif
# 	@export PIPENV_TIMEOUT=7200
# 	@pipenv install --dev    	ipyaggrid

test-coverage:
	-poetry run coverage --rcfile=.coveragerc run -m pytest
	-coveralls

build: requirements.txt
	@poetry build

test: clean
	@poetry run pytest --verbose --durations=0 \
		--cov=penelope \
		--cov-report=term \
		--cov-report=xml \
		--cov-report=html \
		tests

lint:
	@poetry run flake8 --version
	@poetry run flake8
	# @poetry run pylint $(SOURCE_FOLDERS) | sort | uniq | grep -v "************* Module" > pylint.log
	# @poetry run mypy --version
	# @poetry run mypy .

format: clean black isort

isort:
	@poetry run isort $(SOURCE_FOLDERS)

yapf: clean
	@poetry run yapf --version
	@poetry run yapf --in-place --recursive $(SOURCE_FOLDERS)

black:
	@poetry run black --version
	@poetry run black --line-length 120 --target-version py38 \
		--skip-string-normalization $(SOURCE_FOLDERS)

clean:
	@rm -rf .pytest_cache build dist .eggs *.egg-info
	@rm -rf .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output

update:
	@poetry update

install_graphtool:
	@sudo echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt buster main" >> /etc/apt/sources.list
	@sudo apt-key adv --keyserver keys.openpgp.org --recv-key 612DEFB798507F25
	@sudo apt update && apt install python3-graph-tool

requirements.txt: poetry.lock
	@poetry export -f requirements.txt --output requirements.txt

.PHONY: install_lab install_dev nltk_download spacy_download models \
	init lint format yapf black clean \
	test test-coverage update install_graphtool build isort
