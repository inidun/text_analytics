
include .env

.DEFAULT_GOAL=build

install_dev: models install_lab
	@echo "Install dev dependencies"

models: spacy_download nltk_download

spacy_download:
	@pipenv run python -m spacy download en_core_web_sm

nltk_download:
	@pipenv run python -c "import nltk; nltk.download('stopwords')"
	@pipenv run python -c "import nltk; nltk.download('punkt')"

install_lab:
	@pipenv run jupyter labextension install \
    	@jupyter-widgets/jupyterlab-manager \
    	@bokeh/jupyter_bokeh \
    	jupyter-matplotlib \
    	ipyaggrid

.PHONY: install_lab install_dev nltk_download spacy_download models
