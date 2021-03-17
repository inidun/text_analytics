# %%

import itertools
import glob
import os
import re
from typing import List

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)
pd.set_option("max_rows", 10)
# %%


def expand_article_pages(page_ref: str) -> List[int]:
    """['p. D-D', 'p. D', 'p. D, D ', 'p. D, D-D ', 'p.D-D', 'p.D',
    'p. D-D, D ', 'page D', 'p., D-D', 'p. D-D, D-D ']"""
    page_ref = re.sub(r'^(p\.\,?|pages?)', '', page_ref).replace(' ', '').split(',')

    # ix = itertools.chain(
    #     *[range(int(x), int(y)) for x, y in [ (x, x) if '-' not in x else x.split('-') for x in page_ref]]
    # )

    ix = itertools.chain(
        *(
            [list(range(int(x), int(y) + 1)) for x, y in [w.split('-') for w in page_ref if '-' in w]]
            + [[int(x)] for x in page_ref if '-' not in x]
        )
    )

    return list(ix)


def extract_courier_id(eng_host_item: str) -> str:

    m = re.match(r'.*\s(\d+\seng$)', eng_host_item)
    if not m:
        print(eng_host_item)
        return None

    courier_id = m.group(1).replace(' ', '')
    if len(courier_id) < 9:
        courier_id = '0' + courier_id

    return courier_id


def extract_english_host_item(host_item: str) -> str:

    items = [x for x in host_item.split("|") if x.endswith('eng')]
    if len(items) == 0:
        return None

    return items[0]


def create_article_index(filename: str) -> pd.DataFrame:

    df = pd.read_csv(filename, sep=';')

    df.columns = [
        'record_number',
        'catalogue_title',
        'authors',
        'titles_in_other_languages',
        'languages',
        'series',
        'catalogue_subjects',
        'document_type',
        'host_item',
        'publication_date',
        'notes',
    ]

    df = df[df['document_type'] == 'article']
    df = df[df.languages.str.contains('eng')]

    df['eng_host_item'] = df['host_item'].apply(extract_english_host_item)
    df = df.copy()

    df['page_ref'] = df['eng_host_item'].str.extract(
        r'((?:p\.\,?|pages?)(?:\s*\d+(?:-\d+)*)(?:\,\s*\d{1,3}(?:-\d{1,3})*\s)*)'
    )[0]
    df.loc[df.record_number == 187812, 'page_ref'] = 'p. 18-31'
    df.loc[df.record_number == 64927, 'page_ref'] = 'p. 28-29'
    df['courier_id'] = df.eng_host_item.apply(extract_courier_id)

    df['pages'] = df.page_ref.apply(expand_article_pages)
    df['year'] = df.publication_date.apply(lambda x: int(x[:4]))

    return df[
        [
            'record_number',
            'catalogue_title',
            # 'authors',
            # 'titles_in_other_languages',
            # 'languages',
            # 'series',
            # 'catalogue_subjects',
            # 'document_type',
            # 'host_item',
            'eng_host_item',
            'courier_id',
            'year',
            'publication_date',
            'pages',
            'notes',
        ]
    ]


article_index = create_article_index('UNESCO_Courier_metadata.csv')
# article_index.to_csv('UNESCO_Courier_articles_metadata.csv', sep='\t')

# %%


def extract_article_pages(filename: str, pages: List[int], title: str) -> None:
    print(filename, pages, title)
    return (filename, pages, title)


# %%
def extract_articles(folder: str, article_index: pd.DataFrame) -> None:

    missing = set()

    for _, x in article_index.iterrows():

        filename_pattern = os.path.join(folder, f"{x['courier_id']}*.xml")
        filenames = glob.glob(filename_pattern)

        if len(filenames) == 0:
            missing.add(x['courier_id'])
            # print(x['courier_id'], 'no match')
            continue

        if len(filenames) > 1:
            print(x['courier_id'], "ambiguous")
            continue

        # TODO: Check pages for possible mismatch
        # TODO: Check overlapping pages
        # extract_article_pages(filenames[0], x['pages'], x['catalogue_title'])

    print("Missing courier_ids: ", *missing)


extract_articles("./data/xml", article_index)


# %%
teststring = extract_article_pages(next(article_index.iterrows())[1].courier_id, [2, 1], "hello")
# %%

# from jinja2 import Environment, PackageLoader, select_autoescape
# env = Environment(
#     loader=PackageLoader('curation', 'templates'),
#     autoescape=select_autoescape(['html', 'xml'])
# )

# %%

from jinja2 import Template

t = """<?xml version="1.0" encoding="UTF-8"?>
<article>
<filename>{{ filename }}</filename>
<title>{{ title }}</title>
{% for page in pages %}
<page number="{{ page }}">{{ page }}</page>
{%- endfor %}
</article>"""

template = Template(t)
template.render(filename="ha", pages=[1, 2, 3], title="title")

# %%
