import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from preprocess import get_data
from pathlib import Path

# Suggested hyperparameters from the paper
WINDOW_SIZE = 10
EPOCH = 10

# sg=1 so that it's a skip-gram model
model = Word2Vec(window=WINDOW_SIZE, sg=1)

#data needs to be a list of lists of words, where each sublist represents words from one sentence
data = list(get_data(Path('../data/nyt-data-test.txt'), preprocessed=True)) # call preprocess function
model.build_vocab(data)

#model.save("word2vec.model")
model.train(data, total_examples=model.corpus_count, epochs=EPOCH)

# Get word embeddings from the trained model
word_vectors = model.wv

# get_normed_vectors()
# add_vectors() --- this can update the existing vectors

# Get the embedding for a specific word
vector = word_vectors['American']

# Cosine similarity for one vector against a list of other vectors
# return: cosine distance as numpy arrays
word_vectors.cosine_similarities(vector_American, other_vectors)

similar_words = word_vectors.similar_by_vector(vector, topn=10)

# There's also a most_similar function with positive and negative words as inputs

# This should give us the count of this word
word_vectors.vocab['American'].count