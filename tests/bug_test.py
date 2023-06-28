# from typing import Callable, List
# from penelope import pipeline
# import penelope.notebook.topic_modelling as gui
# from penelope.notebook.topic_modelling.load_topic_model_gui import _load_tm_handler
# from penelope.topic_modelling import find_models

# def test_load_predicted_model():
#     ...
#     current_state: Callable[[], gui.TopicModelContainer] = gui.TopicModelContainer.singleton

#     corpus_folder: str = "/data/inidun"
#     corpus_config: pipeline.CorpusConfig = pipeline.CorpusConfig.load('./resources/courier_page.yml')
#     model_infos: List[dict] = find_models(corpus_folder)

#     _load_tm_handler(corpus_config, corpus_folder, current_state(), "courier_issue_50", model_infos)
