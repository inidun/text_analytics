import re

from penelope import corpus as corpora
from penelope import pipeline, utility
from penelope.pipeline import tasks

HYPHEN_REGEXP = re.compile(r'\b(\w+)[-¬]\s*\r?\n\s*(\w+)\s*\b', re.UNICODE)


def remove_hyphens(text: str) -> str:
    result = re.sub(HYPHEN_REGEXP, r"\1\2\n", text)
    return result


def test_remove_hyphens():
    text: str = """The choreo-
 graphy which makes one's
head spin in its com¬
plex pat-

terns has
been evolved through hun-dreds of years
of tra-
    dition and training."""

    result = remove_hyphens(text)

    assert (
        result
        == """The choreography
which makes one's
head spin in its complex
patterns
has
been evolved through hun-dreds of years
of tradition
and training."""
    )


def test_load():
    text_transform_opts = corpora.TextTransformOpts(
        fix_whitespaces=True, fix_hyphenation=True, extra_transforms=[remove_hyphens]
    )
    config: pipeline.CorpusConfig = pipeline.CorpusConfig(
        corpus_name='courier',
        corpus_type=pipeline.CorpusType.Text,
        corpus_pattern='*.zip',
        checkpoint_opts=pipeline.CheckpointOpts(),
        text_reader_opts=corpora.TextReaderOpts(),
        filter_opts=None,
        pipelines={},
        pipeline_payload=pipeline.PipelinePayload(),
        language='english',
        text_transform_opts=text_transform_opts,
    )

    text: str = utility.read_textfile('./tests/test_data/courier/1955_069029_026.txt')

    # config.pipeline_payload.source = [('apa.txt', text)]

    task = tasks.LoadText(
        source=[('apa.txt', text)],
        reader_opts=config.text_reader_opts,
        transform_opts=text_transform_opts,
    )

    p = pipeline.CorpusPipeline(config=config).add(task).setup()

    processed_payload: pipeline.DocumentPayload = p.single()

    # payload: pipeline.DocumentPayload = pipeline.DocumentPayload(
    #     content_type=pipeline.ContentType.TEXT, filename='APA.txt', content=text
    # )
    # processed_payload: pipeline.DocumentPayload = task.process_payload(payload)

    assert processed_payload is not None
