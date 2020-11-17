import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from preprocess import get_data
from pathlib import Path
from words import all_vermin_singulars, all_vermin_plurals_dict, all_target_singulars, all_target_plurals_dict, all_moral_disgust_stem, all_moral_disgust_dict 

from pdb import set_trace as bp


def train(model, data, epoch_num):
    model.build_vocab(data)
    model.train(data, total_examples=model.corpus_count, epochs=epoch_num)
    #model.save("word2vec.model")

    # Get word embeddings from the trained model
    word_vectors = model.wv
    return word_vectors


def normalize(word_vectors):
    # zero-center and normalization
    normalized_vecs = word_vectors.get_normed_vectors()
    centered_vecs = np.subtract(normalized_vecs, np.mean(normalized_vecs, axis=1, keepdims=True))
    keys = word_vectors.index_to_key
    # might also need to check keys 
    word_vectors.add_vectors(keys, centered_vecs, replace=True)
    return word_vectors


def get_cosine_distance(normalized_word_vectors, sentiment_words, target_words):
    """
    TODO
    - use frequency to calculate weighted vector for a target word and its morphological friends
    - and then use these weighted vectors for cosine similarity
    """

    # vector_american = word_vectors['american']
    # vector_japanese = word_vectors['japanese']
    # vector_plant = word_vectors['plant']
    #count = word_vectors.get_vecattr('american', 'count')
    # dist_j = word_vectors.cosine_similarities(vector_american, [vector_japanese])
    # dist_p = word_vectors.cosine_similarities(vector_american, [vector_plant])

    all_distances = {}
    all_similar_words = {}

    # Construct a list of word embeddings for the sentiiment words 
    sentiment_word_vectors = [] 
    for sentiment_word in sentiment_words:
        sentiment_word_vectors.append(normalized_word_vectors[sentiment_word])

    # Calculates cosine similarity between target word and all the sentiment words
    for word in target_words:
        word_vector = normalized_word_vectors[word]
        word_count = normalized_word_vectors.get_vecattr(word, 'count')

        # TODO: weighted vector!

        distance_list = normalized_word_vectors.cosine_similarities(word_vector, sentiment_word_vectors)
        all_distances[word] = distance_list
    
        # Find top 5 similar words for each target word
        similar_words = normalized_word_vectors.similar_by_vector(word_vector, topn=5)
        all_similar_words[word] = similar_words

        # There's also a most_similar function with positive and negative words as inputs
    
    return all_distances, all_similar_words


def main():
    # Suggested hyperparameters from the paper
    WINDOW_SIZE = 10
    EPOCH = 10

    sentiment_words = all_moral_disgust_stem
    target_words = all_target_singulars

    # sg=1 so that it's a skip-gram model
    model = Word2Vec(window=WINDOW_SIZE, sg=1, min_count=1)
    
    #data needs to be a list of lists of words, where each sublist represents words from one sentence
    data = list(get_data(Path('../data/nyt-data-test.txt'), preprocessed=False)) # call preprocess function

    word_vectors = train(model, data, EPOCH)
    normalized_vectors = normalize(word_vectors)

    all_distances, all_similar_words = get_cosine_distance(normalized_vectors , sentiment_words, target_words)
    print(all_similar_words)



if __name__ == '__main__':
    main()