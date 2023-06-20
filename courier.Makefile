SHELL=/bin/bash

COURIER_VERSION=v0.2.0
CORPUS_NAME=courier

today=$(shell date '+%Y%m%d')

DATA_FOLDER=/data/inidun

CORPUS_FOLDER=$(DATA_FOLDER)/${CORPUS_NAME}/corpus/$(COURIER_VERSION)
CORPUS_FILENAME=$(CORPUS_FOLDER)/article_corpus.zip
CONFIG_FILENAME=$(CORPUS_FOLDER)/courier_article.yml
FEATHER_FOLDER=$(CORPUS_FOLDER)/article_corpus.feather

ifeq (,$(wildcard $(CORPUS_FOLDER)))
$(error Corpus folder $(CORPUS_FOLDER) not found.)
endif

ifeq (,$(wildcard $(CONFIG_FILENAME)))
$(error Corpus config $(CONFIG_FILENAME) not found.)
endif


# ##########################################################################################################
# # Default part-of-speech recepi
# ##########################################################################################################

.PHONY: pos-tag
pos-tag: data_dirs
	@PYTHONPATH=. poetry run python scripts/courier_pos_tag.py $(CONFIG_FILENAME)

# ##########################################################################################################
# # Default DTM recepi
# ##########################################################################################################

DTM_FOLDER=$(DATA_FOLDER)/${CORPUS_NAME}/dtm/$(COURIER_VERSION)
DTM_MIN_WORD_LENGTH=2
DTM_MAX_TOKENS=2000000
DTM_DESERIALIZE_PROCESSES=1

.PHONY: vectorize
vectorize:
	@mkdir -p $(DTM_FOLDER)/logs
	@PYTHONPATH=. poetry run vectorize \
		--to-lower \
		--lemmatize \
		--max-tokens $(DTM_MAX_TOKENS) \
		--min-word-length $(DTM_MIN_WORD_LENGTH) \
		--deserialize-processes $(DTM_DESERIALIZE_PROCESSES) \
		--filename-pattern '**/*.feather' \
		$(CONFIG_FILENAME) \
		$(FEATHER_FOLDER) \
		$(DTM_FOLDER) \
		dtm_full_$(DTM_MAX_TOKENS) \
			&>> $(DTM_FOLDER)/logs/dtm_$(today).log

# ##########################################################################################################
# # Default TM recepi
# ##########################################################################################################

X=apa-%.txt
NS := 50 100 200 500

TM_FOLDER=$(DATA_FOLDER)/${CORPUS_NAME}/tm/$(COURIER_VERSION)
TM_MINIMUM_PROBABILITY=0.02
TM_MAX_ITER=3000
TM_MAX_TOKENS=500000
TM_MIN_TF=5
TM_ENGINE=gensim_mallet-lda
TM_WORKERS=1
TM_LOWERCASE=yes
TM_LEMMATIZE=

TM_NAME := tm_courier_$(COURIER_VERSION)_%
TM_OPTS :=

ifneq ($(TM_MIN_TF),)
	TM_NAME := $(TM_NAME)-TF$(TM_MIN_TF)
	TM_OPTS := $(TM_OPTS) --tf-threshold $(TM_MIN_TF)
endif

ifneq ($(TM_MINIMUM_PROBABILITY),)
	TM_NAME := $(TM_NAME)-MP$(TM_MINIMUM_PROBABILITY)
	TM_OPTS := $(TM_OPTS) --minimum-probability $(TM_MINIMUM_PROBABILITY)
endif

ifneq ($(TM_MAX_TOKENS),)
	TM_NAME := $(TM_NAME)-$(TM_MAX_TOKENS)
	TM_OPTS := $(TM_OPTS) --max-tokens $(TM_MAX_TOKENS)
endif

ifeq ($(TM_LOWERCASE),yes)
	TM_NAME := $(TM_NAME)-lc
	TM_OPTS := $(TM_OPTS) --to-lower
endif

ifeq ($(TM_LEMMATIZE),yes)
	TM_NAME := $(TM_NAME)-lemma
	TM_OPTS := $(TM_OPTS) --lemmatize
endif

TM_NAME := $(TM_NAME).$(TM_ENGINE)

default-topic-models: $(patsubst %,$(TM_FOLDER)/$(TM_NAME),$(NS))
$(TM_FOLDER)/$(TM_NAME):
	@PYTHONPATH=. tm-train \
		--corpus-source $(CORPUS_FILENAME) \
		--target-folder $(TM_FOLDER) \
		--n-topics $* \
		--alpha asymmetric \
		--engine $(TM_ENGINE) \
		$(TM_OPTS) \
		--max-iter $(TM_MAX_ITER) \
		--pos-excludes 'PUNCT' \
		--random-seed 42 \
		--target-mode both \
		--workers $(TM_WORKERS) \
		$(CONFIG_FILENAME) \
		$@

# --num-top-words 500 \
# --filename_pattern null \
