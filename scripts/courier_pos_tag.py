import os
import re

import click
import spacy
from penelope.corpus import TextTransformOpts
from penelope.pipeline import DEFAULT_TAGGED_FRAMES_FILENAME_SUFFIX, CorpusConfig, CorpusPipeline
from penelope.utility import path_add_suffix
from spacy.language import Language

SPACY_TAGGED_COLUMNS: dict = dict(
    text_column='text',
    lemma_column='lemma_',
    pos_column='pos_',
)


HYPHEN_REGEXP = re.compile(r'\b(\w+)[-¬]\s*\r?\n\s*(\w+)\s*\b', re.UNICODE)


def remove_hyphens(text: str) -> str:
    result = re.sub(HYPHEN_REGEXP, r"\1\2\n", text)
    return result


@click.command()
@click.argument('config-filename', type=click.STRING)
def main(config_filename: str = None):

    en_nlp: Language = spacy.load(os.path.join(os.environ.get("SPACY_DATA", ""), "en_core_web_sm"))

    text_transform_opts = TextTransformOpts(
        fix_hyphenation=False, fix_whitespaces=True, fix_accents=True, extra_transforms=[remove_hyphens]
    )

    attributes = ['text', 'lemma_', 'pos_']
    config: CorpusConfig = CorpusConfig.load(path=config_filename)
    tagged_frames_filename: str = os.path.abspath(
        path_add_suffix(config.pipeline_payload.source, DEFAULT_TAGGED_FRAMES_FILENAME_SUFFIX)
    )

    pipeline = (
        CorpusPipeline(config=config)
        .load_text(reader_opts=config.text_reader_opts, transform_opts=text_transform_opts)
        .set_spacy_model(en_nlp)
        .text_to_spacy()
        .spacy_to_tagged_frame(attributes=attributes)
        .checkpoint(filename=tagged_frames_filename)
    )

    _ = pipeline.exhaust()


if __name__ == "__main__":
    main()
