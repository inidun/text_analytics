import gensim
import text_analytic_tools.text_analysis.engine_options as options
import text_analytic_tools.text_analysis.utility as utility
import text_analytic_tools.utility as utils

logger = utils.getLogger("text_analytic_tools")

def compute_score(id2word, model, corpus):
    try:
        dictionary = utility.create_dictionary(id2word)
        coherence_model =  gensim.models.CoherenceModel(model=model, corpus=corpus, dictionary=dictionary, coherence='u_mass')
        coherence_score = coherence_model.get_coherence()
    except Exception as ex:
        logger.error(ex)
        coherence_score = None
    return coherence_score

def compute_scores(method, id2word, corpus, start=10, stop=20, step=10, engine_args=None):

    algorithm_name = method.split('_')[1].upper()

    metrics = []

    dictionary = utility.create_dictionary(id2word)

    for num_topics in range(start, stop, step):

        algorithm = options.engine_options(algorithm_name, corpus, id2word, engine_args)

        engine = algorithm['engine']
        engine_options = algorithm['options']

        model = engine(**engine_options)

        coherence_score = gensim.models.CoherenceModel(model=model, corpus=corpus, dictionary=dictionary, coherence='u_mass')

        perplexity_score = 2 ** model.log_perplexity(corpus, len(corpus))

        metric = dict(
            num_topics=num_topics,
            coherence_score=coherence_score,
            perplexity_score=perplexity_score
        )
        metrics.append(metric)

    # filename = os.path.join(target_folder, "metric_scores.json")

    # with open(filename, 'w') as fp:
    #     json.dump(model_data.options, fp)

    return metrics

# Can take a long time to run.
# model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=data_lemmatized, start=2, limit=40, step=6)
# # Show graph
# limit=40; start=2; step=6;
# x = range(start, limit, step)
# plt.plot(x, coherence_values)
# plt.xlabel("Num Topics")
# plt.ylabel("Coherence score")
# plt.legend(("coherence_values"), loc='best')
# plt.show()

