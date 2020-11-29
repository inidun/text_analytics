import os

from penelope.corpus.readers import TextTransformOpts
from penelope.pipeline import CorpusConfig, SpacyPipeline

from notebooks.corpus_data_config import SSI

CORPUS_FOLDER = './tests/test_data'
OUTPUT_FOLDER = './tests/output'


def test_create_pos_checkpoint_pipeline() -> SpacyPipeline:

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    data_folder: str = CORPUS_FOLDER
    ssi: CorpusConfig = SSI.set_folder(data_folder)
    checkpoint_filename: str = os.path.join(OUTPUT_FOLDER, 'ssi_pos_csv.zip')

    # pipeline = create_pos_checkpoint_pipeline(config=ssi, checkpoint_filename=checkpoint_filename)

    # pipeline.exhaust()

    assert os.path.isfile(checkpoint_filename)
