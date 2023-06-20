import os

import click  # pylint: disable=unused-import
from penelope.corpus import TextTransformOpts
from penelope.pipeline import DEFAULT_TAGGED_FRAMES_FILENAME_SUFFIX, CorpusConfig, CorpusPipeline
from penelope.utility import load_cwd_dotenv, path_add_suffix


@click.command()
@click.argument('config-filename', type=click.STRING)
def main(config_filename: str = None):  # pylint: disable=redefined-outer-name
    load_cwd_dotenv()

    transform_opts = TextTransformOpts(transforms="normalize-whitespaces,dehyphen,strip-accents")

    config: CorpusConfig = CorpusConfig.load(path=config_filename)

    tagged_corpus_source: str = os.path.abspath(
        path_add_suffix(config.pipeline_payload.source, DEFAULT_TAGGED_FRAMES_FILENAME_SUFFIX)
    )

    pipeline = (
        CorpusPipeline(config=config)
        .load_text(reader_opts=config.text_reader_opts, transform_opts=transform_opts)
        .to_tagged_frame(tagger=config.resolve_dependency('tagger'))
        .checkpoint(filename=tagged_corpus_source)
        .checkpoint_feather(folder=config.checkpoint_opts.feather_folder, force=True)
    )

    _ = pipeline.exhaust()


if __name__ == "__main__":
    # config_filename = './opts/inidun/configs/courier_article.yml'
    # main(config_filename=config_filename)
    main()
