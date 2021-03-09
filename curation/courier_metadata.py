# %%

from typing import List
import re
import pandas as pd
import itertools

from pytz import AmbiguousTimeError

pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)
pd.set_option("max_rows", None)
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

    df['eng_host_item'] = df['host_item'].apply(lambda x: x.split('|')[0])
    df['page_ref'] = df['eng_host_item'].str.extract(
        r'((?:p\.\,?|pages?)(?:\s*\d+(?:-\d+)*)(?:\,\s*\d{1,3}(?:-\d{1,3})*\s)*)'
    )[0]
    df.loc[df.record_number == 187812, 'page_ref'] = 'p. 18-31'
    df.loc[df.record_number == 64927, 'page_ref'] = 'p. 28-29'
    df['courier_id'] = df['eng_host_item'].str.extract(r'(\s\d+\seng$)').replace(' ', '')

    df['pages'] = df.page_ref.apply(expand_article_pages)
    df['year'] = df.publication_date.apply(lambda x: int(x[:4]))

    return df[[
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
    ]]

def extract_article_pages():
    pass

def extract_articles(folder: str, article_index: pd.DataFrame) -> None:
    
    for x in article_index.iteritems():

        filename_pattern = os.path.join(folder, f"{x['courier_id']}*.txt")
        filenames = glob.glob(filename_pattern)

        if len(filenames) == 0:
            print('no match')
            continue

        if len(filenames) > 1:
            print("AmbiguousTimeError")
            continue

        extract_article_pages(filenames[0], x['pages'], x['title'])

df = create_article_index('UNESCO_Courier_metadata.csv')
df.to_csv('UNESCO_Courier_articles_metadata.csv', sep='\t')

# %%
#import ast
#ast.literal_eval('[0,1,2,3,4 5]'

# %%
