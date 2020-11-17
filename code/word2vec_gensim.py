import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from preprocess import get_data
from pathlib import Path
from words import all_vermin_singulars, all_vermin_plurals_dict, all_target_singulars, all_target_plurals_dict

from pdb import set_trace as bp

# Suggested hyperparameters from the paper
WINDOW_SIZE = 10
EPOCH = 10

# sg=1 so that it's a skip-gram model
model = Word2Vec(window=WINDOW_SIZE, sg=1, min_count=1)

#data needs to be a list of lists of words, where each sublist represents words from one sentence
data = list(get_data(Path('../data/nyt-data-test.txt'), preprocessed=False)) # call preprocess function
model.build_vocab(data)

#model.save("word2vec.model")
model.train(data, total_examples=model.corpus_count, epochs=EPOCH)

# Get word embeddings from the trained model
word_vectors = model.wv

# zero-center and normalization
normalized_vecs = word_vectors.get_normed_vectors()
centered_vecs = np.subtract(normalized_vecs, np.mean(normalized_vecs, axis=1))
# normalized_vecs = np.divide(word_vectors, np.sum(centered_vecs, axis=1))

keys = word_vectors.index_to_key
# might need to check if the entire matrix is added,
# or we need a for loop to add each one...
# might also need to check keys 
word_vectors.add_vectors(keys, centered_vecs, replace=True)

# Get the embedding for a specific word
vector_american = word_vectors['american']
vector_japanese = word_vectors['japanese']
vector_plant = word_vectors['plant']

# Cosine similarity for one vector against a list of other vectors
# return: cosine distance as numpy arrays
dist_j = word_vectors.cosine_similarities(vector_american, [vector_japanese])
dist_p = word_vectors.cosine_similarities(vector_american, [vector_plant])
print(dist_j)
print(dist_p)
print("------")

similar_words = word_vectors.similar_by_vector(vector_american, topn=10)
print(similar_words)
print("-------")

# There's also a most_similar function with positive and negative words as inputs

# This should give us the count of this word
count = word_vectors.vocab['american'].count
print("count of 'american': " + str(count))
