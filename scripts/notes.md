## TODO

### New tools

- [ ] [Notebook with collocate measuring tool · Issue #8](https://github.com/inidun/tasks/issues/8)
- [ ] [Notebook with most discriminating terms · Issue #9](https://github.com/inidun/tasks/issues/9)

### POS

- [ ] Add tab: line diagram
- [ ] Add tab: bar diagram

### Improvements

- [ ] Change colors in plot
- [ ] Add ipyaggrid to Pipfile
- [ ] Add new graphs, e.g. rolling average

### Other

- [ ] Add flake

---

## Commands

### Install Node using [NVM](https://github.com/nvm-sh/nvm#installing-and-updating)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
nvm ls-remote
nvm install v14.10.1
```

### Install labextensions

```
jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @bokeh/jupyter_bokeh \
    jupyter-matplotlib \
    ipyaggrid

jupyter labextension update --all
jupyter lab build
```

### Install needed nltk package:

```python
nltk.download('punkt')
```

### Filename patterns, example

- `DECLARATION_0201_013175_1995.txt`
- `CONVENTION_0201_015241_1971_paris.txt`

### Run vectorize script

```bash
python scripts/vectorize_corpus.py \    
    --to-lower \
    --no-remove-accents \
    --min-length 2 \
    --keep-numerals \
    --no-keep-symbols \
    --only-alphanumeric \
    --file-pattern '*.txt' \
    --meta-field "document_type:_:0" \    
    --meta-field "document_id:_:2" \
    --meta-field "year:_:3" \
    ./data/legal_instrument_corpus.txt.zip \
    ./data \
```
alt

```bash
python scripts/vectorize_corpus.py  --to-lower --no-remove-accents --min-length 2 --keep-numerals --no-keep-symbols --only-alphanumeric --file-pattern '*.txt' --meta-field "document_type:_:0" --meta-field "document_id:_:2" --meta-field "year:_:3" ./data/legal_instrument_corpus.txt.zip ./data
```
