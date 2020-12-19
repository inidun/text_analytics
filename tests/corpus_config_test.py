from penelope.corpus.readers.interfaces import TextReaderOpts
from penelope.pipeline import CorpusConfig, PipelinePayload


def test_corpus_config_set_folder():

    config: CorpusConfig = CorpusConfig(
        text_reader_opts=TextReaderOpts(),
        pipeline_payload=PipelinePayload(
            source="corpus.zip",
            document_index_source="document_index.csv",
        ),
    ).folder('/data')

    assert config.pipeline_payload.source == '/data/corpus.zip'
    assert config.pipeline_payload.document_index_source == '/data/document_index.csv'


# def test_corpus_config_dump():
#     config = CorpusConfig.load('./data/ssi_corpus_config.yaml')
#     config.dump('./data/ssi_corpus.config.yaml')
