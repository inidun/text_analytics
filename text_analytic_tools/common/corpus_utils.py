import zipfile
import pandas as pd
import text_analytic_tools.utility as utility

logger = utility.getLogger("text_analytic_tools")

def store_tokenized_corpus_as_archive(tokenized_docs, target_filename):
    """Stores a tokenized (string) corpus to a zip archive

    Parameters
    ----------
    tokenized_docs : [type]
        [description]
    corpus_source_filepath : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    file_stats = []
    process_count = 0

    # TODO: Enable store of all documents line-by-line in a single file
    with zipfile.ZipFile(target_filename, "w") as zf:

        for document_id, document_name, chunk_index, tokens in tokenized_docs:

            text = ' '.join([ t.replace(' ', '_') for t in tokens ])
            store_name  = utility.path_add_sequence(document_name, chunk_index, 4)

            zf.writestr(store_name, text, zipfile.ZIP_DEFLATED)

            file_stats.append((document_id, document_name, chunk_index, len(tokens)))

            if process_count % 100 == 0:
                logger.info('Stored {} files...'.format(process_count))

            process_count += 1


    df_summary = pd.DataFrame(file_stats, columns=['document_id', 'document_name', 'chunk_index', 'n_tokens'])

    return df_summary

