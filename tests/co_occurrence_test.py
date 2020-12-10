import os

from penelope.co_occurrence import ContextOpts
from penelope.corpus import TokensTransformOpts
from penelope.corpus.readers import ExtractTaggedTokensOpts, TaggedTokensFilterOpts
from penelope.pipeline.config import CorpusConfig
from penelope.utility.pos_tags import PoS_Tag_Scheme, PoS_Tag_Schemes, pos_tags_to_str

from penelope.pipeline.spacy.spacy_pipelines import spaCy_co_occurrence_pipeline
from notebooks.corpus_data_config import SSI


def test_spaCy_co_occurrence_pipeline():

    checkpoint_filename: str = "./data/SSI_2020_1207_pos_csv.zip"
    if os.path.isfile(checkpoint_filename):
        os.remove(checkpoint_filename)

    ssi: CorpusConfig = SSI(corpus_folder='./data')
    pos_scheme: PoS_Tag_Scheme = PoS_Tag_Schemes.Universal
    tokens_transform_opts: TokensTransformOpts = TokensTransformOpts()
    extract_tagged_tokens_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(
        lemmatize=True, pos_includes=pos_tags_to_str(pos_scheme.Adjective + pos_scheme.Verb + pos_scheme.Noun)
    )
    tagged_tokens_filter_opts: TaggedTokensFilterOpts = TaggedTokensFilterOpts(
        is_space=False,
        is_punct=False,
    )
    context_opts: ContextOpts = ContextOpts(context_width=4)
    global_threshold_count: int = 1
    partition_column: str = 'year'

    co_occurrence = spaCy_co_occurrence_pipeline(
        corpus_config=ssi,
        tokens_transform_opts=tokens_transform_opts,
        extract_tagged_tokens_opts=extract_tagged_tokens_opts,
        tagged_tokens_filter_opts=tagged_tokens_filter_opts,
        context_opts=context_opts,
        global_threshold_count=global_threshold_count,
        partition_column=partition_column,
        checkpoint_filename=checkpoint_filename,
    ).value()

    co_occurrence.to_csv('SSI-co-occurrence-JJVBNN-window-9.csv', sep='\t')

    assert co_occurrence is not None
