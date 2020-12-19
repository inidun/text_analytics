# from unittest.mock import MagicMock, Mock, create_autospec, patch

# import ipyfilechooser
# import ipywidgets
# import penelope.notebook.gui_base as gui_base
# import penelope.utility as utility
# from penelope.pipeline.config import CorpusConfig, CorpusType
# from penelope.utility.pos_tags import PoS_Tag_Schemes


# @patch('ipyfilechooser.FileChooser', Mock(spec=ipyfilechooser.FileChooser))
# @patch(
#     'penelope.utility.get_pos_schema',
#     create_autospec(
#         utility.get_pos_schema,
#         return_value=PoS_Tag_Schemes.Universal,
#     ),
# )
# def test_create():

#     config = Mock(
#         spec=CorpusConfig,
#         **{
#             'corpus_pattern.return_value': "*.zip",
#             'corpus_type.return_value': 5 CorpusType.Pipeline,
#         },
#     )
#     w = (
#         gui_base.BaseGUI()
#         .setup(
#             config=config,
#             compute_callback=lambda _x: _x,
#         )
#         .layout()
#     )

#     assert isinstance(w, ipywidgets.CoreWidget)
