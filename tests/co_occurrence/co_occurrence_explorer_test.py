# import ipywidgets as widgets
# # import penelope import co_occurrence
# # import penelope.notebook.co_occurrence as explore_gui
# # from penelope.notebook.co_occurrence import main_gui

# view = widgets.Output(layout={'border': '2px solid green'})


# # FIXME Penelope only test, remove or move
# # def test_create_co_occurrence_explorer_gui():

# #     corpus_filename: str = './tests/test_data/VENUS/VENUS_co-occurrence.csv.zip'
# #     bundle: co_occurrence.Bundle = co_occurrence.Bundle.load(corpus_filename, compute_frame=False)

# #     trends_data = main_gui.to_trends_data(bundle).update()
# #     gui_explore: explore_gui.ExploreGUI = explore_gui.ExploreGUI(bundle=bundle).setup().display(trends_data=trends_data)

# #     assert gui_explore is not None


# def generic_patch(return_value):
#     def _generic_patch(*x, **y):  # pylint: disable=unused-argument
#         return return_value

#     return _generic_patch
