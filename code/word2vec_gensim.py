import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from preprocess import get_data
from pathlib import Path
from words import all_vermin_singulars, all_vermin_plurals_dict, all_target_singulars, all_target_plurals_dict, all_moral_disgust_stem, all_moral_disgust_dict 

from pdb import set_trace as bp

# --------------- Parameters  -----------------
DATA_PATH = '../data/nyt-data-test.txt'
COUNT_PARAM_NAME = 'count'

LABEL_PARAM_VERMIN = 'vermin'
LABEL_PARAM_MORAL_DISGUST = 'moral_disgust'
# TODO: add a label for the other categories when they are added to words.py

# Change this to get cosine similarities for different groups of dehumanizing words
# Options: vermin, moral_disgust
SENTIMENT_LABEL = LABEL_PARAM_MORAL_DISGUST

# Suggested model hyperparameters from the paper
WINDOW_SIZE = 10
EPOCH = 10
# ---------------------------------------------


def train(model, data, epoch_num):
    model.build_vocab(data)
    model.train(data, total_examples=model.corpus_count, epochs=epoch_num)
    #model.save("word2vec.model")

    # Get word embeddings from the trained model
    word_vectors = model.wv
    return word_vectors


def normalize(word_vectors):
    # zero-centering and normalization
    normalized_vecs = word_vectors.get_normed_vectors()
    centered_vecs = np.subtract(normalized_vecs, np.mean(normalized_vecs, axis=1, keepdims=True))
    keys = word_vectors.index_to_key
    # TODO: might also need to check keys 
    word_vectors.add_vectors(keys, centered_vecs, replace=True)
    return word_vectors


def get_weighted_vector(word_vectors, word, main_list, morph_forms_dict):
    """
    Input: a word that we want to find all of its morphological forms 
    Output: a weighted average word vector for all the morphological forms, based on frequency
    """
    print(word)

    count_dict = {}
    vector_dict = {}
    total_count = 0
    try:
        main_count = word_vectors.get_vecattr(word, COUNT_PARAM_NAME)
    except:
        return

    count_dict[word] = main_count
    vector_dict[word] = word_vectors[word]

    for morph_form in morph_forms_dict[word]:
        try:
            count_for_this_form = word_vectors.get_vecattr(morph_form, COUNT_PARAM_NAME)
        except:
            continue 
        count_dict[morph_form] = count_for_this_form
        total_count += count_for_this_form
        vector_dict[morph_form] = word_vectors[morph_form]
    

    #TODO: need to write the weighted sum calculation here

    all_counts = np.asarray(list(count_dict.values()))
    vector_weights = np.divide(all_counts, total_count)
    print(vector_weights.shape)

    all_vectors = np.asarray(list(vector_dict.values()))
    print(all_vectors.shape)
    bp()
    weighted_vector = np.average(all_vectors, axis=0, weights=vector_weights)

    print(weighted_vector)
    print(weighted_vector.shape)
    bp()
    return weighted_vector



def get_sentiment_list_and_dict():
    """
    Returns the list of main sentiment words and its corresponding morphological dictionary
    based on the label set to SENTIMENT_LABEL (at the top of the file)
    """
    sentiment_list_switcher = {
        LABEL_PARAM_MORAL_DISGUST : all_moral_disgust_stem,
        LABEL_PARAM_VERMIN : all_vermin_singulars
    }
    sentiment_dict_switcher = {
        LABEL_PARAM_MORAL_DISGUST : all_moral_disgust_dict,
        LABEL_PARAM_VERMIN : all_vermin_plurals_dict
    }
    sentiment_words = sentiment_list_switcher.get(SENTIMENT_LABEL)
    sentiment_dict = sentiment_dict_switcher.get(SENTIMENT_LABEL)

    return sentiment_words, sentiment_dict


def get_cosine_distance(normalized_word_vectors, sentiment_words, sentiment_dict, target_words):
    """
    Calculates the cosine distance between all the target words with all the sentiment words.
    This function uses the get_weighted_vector helper function to compute a weighted average 
    word vector for each word based on its morphological variations.

    Input:
    - normalized_word_vectors: all word vectors after normalization
    - sentiment_words: a list of all the main sentiment words 
    - sentiment_dict: a dictionary that maps each of the sentiment word to its morphological variations
    - target_words: a list of all the target words for population we are investigating  
    """

    all_distances = {}
    all_similar_words = {}

    # Construct a list of word embeddings for the sentiiment words 
    # This list of vectors are the results of the weighted average calculation based on morphological form variation
    sentiment_word_vectors = [] 
    for sentiment_word in sentiment_words:
        weighted_vector = get_weighted_vector(normalized_word_vectors, sentiment_word, sentiment_words, sentiment_dict)
        #sentiment_word_vectors.append(normalized_word_vectors[sentiment_word])
        sentiment_word_vectors.append(weighted_vector)
    
    print(len(sentiment_word_vectors))
    bp()

    # Calculates cosine similarity between target word and all the sentiment words
    for word in target_words:
        #weighted_word_vector = get_weighted_vector(normalized_word_vectors, word, target_words, sentiment_dict) 
        weighted_word_vector = get_weighted_vector(normalized_word_vectors, 'japanese', target_words, sentiment_dict) 

        distance_list = normalized_word_vectors.cosine_similarities(weighted_word_vector, sentiment_word_vectors)
        all_distances[word] = distance_list
    
        # Find top 5 similar words for each target word
        similar_words = normalized_word_vectors.similar_by_vector(weighted_word_vector, topn=5)
        all_similar_words[word] = similar_words

        # There's also a most_similar function with positive and negative words as inputs
    
    return all_distances, all_similar_words


def main():
    # sg=1 so that it's a skip-gram model
    model = Word2Vec(window=WINDOW_SIZE, sg=1, min_count=1)
    
    #data needs to be a list of lists of words, where each sublist represents words from one sentence
    data = list(get_data(Path(DATA_PATH), preprocessed=False)) # call preprocess function

    word_vectors = train(model, data, EPOCH)
    normalized_vectors = normalize(word_vectors)

    sentiment_words, sentiment_dict = get_sentiment_list_and_dict()
    target_words = all_target_singulars

    all_distances, all_similar_words = get_cosine_distance(normalized_vectors, sentiment_words, sentiment_dict, target_words)
    print(all_similar_words)



if __name__ == '__main__':
    main()