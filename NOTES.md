


## HOWTOs

### PoS tag Courier


```bash
PYTHONPATH=. python scripts/courier_pos_tag.py resources/courier_page.yml
```

### Run vectorize script

```bash
vectorize-corpus \
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
