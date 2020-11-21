import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from preprocess import get_data
from pathlib import Path
from words import all_vermin_singulars, all_vermin_plurals_dict, all_target_singulars, all_target_plurals_dict, all_moral_disgust_stem, all_moral_disgust_dict 
import pandas as pd
import sys, getopt

from pdb import set_trace as bp

# --------------- Parameters  -----------------
LEXICON_PATH = '../data/NRC-VAD-Lexicon.txt'
COUNT_PARAM_NAME = 'count'

def get_weighted_vector(word_vectors, words, morph_forms_dict):
    """
    Created a weighted average vector for all the input words and their related 
    morphological forms. 
    
    Input: 
     - words: A list of words, such as ['lesbian', 'gay', 'bisexual', 'transgender']
     - morph_forms_dict: A dictionary of words to their morphologically related words.
    Output: a weighted average word vector for all the morphological forms, based on frequency
    """
    count_dict = {}
    vector_dict = {}
    total_count = 0

    for word in words:
        morph_forms = morph_forms_dict.get(word)
        if morph_forms != None: # look through morphological forms
            for morph_form in morph_forms_dict[word]:
                try:
                    count_for_this_form = word_vectors.get_vecattr(morph_form, COUNT_PARAM_NAME)
                except:
                    continue 
                count_dict[morph_form] = count_for_this_form
                total_count += count_for_this_form
                vector_dict[morph_form] = word_vectors[morph_form]

        # look at stem
        try:
            count_for_this_form = word_vectors.get_vecattr(word, COUNT_PARAM_NAME)
        except:
            continue 
        count_dict[word] = count_for_this_form
        total_count += count_for_this_form
        vector_dict[word] = word_vectors[word]
    

    # weighted sum calculation 
    all_counts = np.asarray(list(count_dict.values()))
    vector_weights = np.divide(all_counts, total_count)

    all_vectors = np.asarray(list(vector_dict.values()))
    weighted_vector = np.average(all_vectors, axis=0, weights=vector_weights)

    return weighted_vector

# Section 3.1.3 -- Negative Evaluation of a Target Group: Word Embedding Neighbor Valence
def negative_evaluation(wv, target_terms, lexicon, target_forms_dict, n=500):
    '''
    Performs Section 3.1.3 of the paper. Identify the n nearest terms to the weighted average of the target terms. 
    Return a weighted average of the valence of the n nearest neighbors. 

    Parameters:
        - wv: The normalized and zero-center word vectors, a KeyedVectors object. 
        - target_terms: A list of target terms, such as ['lesbian', 'gay', 'bisexual', 'transgender']
        - lexicon: The NRC-VAD lexicon, a Pandas DataFrame.
        - target_forms_dict: A dictionary of words to their morphologically related words.
        - n: Number of nearest neighbors. 

    Returns the weighted average valence of the n nearest neighbors, a float. 
    '''
    # create target_term vector
    target_vec = get_weighted_vector(wv, target_terms, target_forms_dict)
    similar_words = wv.similar_by_vector(target_vec, topn=n)

    similar_words_lexicon = lexicon[lexicon['Word'].isin(similar_words)]

    count = []
    for word in similar_words_lexicon.Word:
        try:
            count.append(wv.get_vecattr(row.Word, COUNT_PARAM_NAME))
        except:
            count.append(0) 

    similar_words_lexicon["Count"] = count 
    similar_words_lexicon["Weight"] = similar_words_lexicon["Count"] / similar_words_lexicon["Count"].sum()
    similar_words_lexicon["Weighted_Valence"] = similar_words_lexicon.apply(lambda row: row.Valence * row.Weight, axis=1)

    return similar_words_lexicon["Weighted_Valence"].sum()

# Section 3.2.3 -- Denial of Agency: Word Embedding Neighbor Dominance
def denial_of_agency(wv, target_terms, lexicon, target_forms_dict, n=500):
    '''
    Performs Section 3.2.3 of the paper. Identify the n nearest terms to the weighted average of the target terms. 
    Return a weighted average of the valence of the n nearest neighbors. 

    Parameters:
        - wv: The normalized and zero-center word vectors, a KeyedVectors object. 
        - target_terms: A list of target terms, such as ['lesbian', 'gay', 'bisexual', 'transgender']
        - lexicon: The NRC-VAD lexicon, a Pandas DataFrame.
        - target_forms_dict: A dictionary of words to their morphologically related words.
        - n: Number of nearest neighbors. 
        
    Returns the weighted average valence of the n nearest neighbors, a float. 
    '''
     # create target_term vector
    target_vec = get_weighted_vector(wv, target_terms, target_forms_dict)
    similar_words = wv.similar_by_vector(target_vec, topn=n)

    similar_words_lexicon = lexicon[lexicon['Word'].isin(similar_words)]

    count = []
    for word in similar_words_lexicon.Word:
        try:
            count.append(wv.get_vecattr(row.Word, COUNT_PARAM_NAME))
        except:
            count.append(0) 

    similar_words_lexicon["Count"] = count 
    similar_words_lexicon["Weight"] = similar_words_lexicon["Count"] / similar_words_lexicon["Count"].sum()
    similar_words_lexicon["Weighted_Dominance"] = similar_words_lexicon.apply(lambda row: row.Dominance * row.Weight, axis=1)

    return similar_words_lexicon["Weighted_Dominance"].sum()

# Section 3.3 -- Moral Disgust
def moral_disgust(wv, target_terms, target_forms_dict):
    '''
    Performs Section 3.3 of the paper. Compute cosine similarity between a target 
    vector and a moral disgust vector. 

    Parameters:
        - wv: The normalized and zero-center word vectors, a KeyedVectors object. 
        - target_terms: A list of target terms, such as ['lesbian', 'gay', 'bisexual', 'transgender']
        - target_forms_dict: A dictionary of words to their morphologically related words.
        
    Returns the cosine similarity between a target vector and a moral disgust vector.
    '''
    # create moral disgust weighted average vector 
    moral_disgust_vec = get_weighted_vector(wv, all_moral_disgust_stem, all_moral_disgust_dict)
    # create target_term vector
    target_vec = get_weighted_vector(wv, target_terms, target_forms_dict)
    return wv.cosine_similarities(target_vec, [moral_disgust_vec])

# Section 3.4 -- Vermin as a Dehumanizing Metaphor 
def vermin(wv, target_term):
    '''
    Performs Section 3.3 of the paper. Compute cosine similarity between a target 
    vector and a vermin vector. 

    Parameters:
        - wv: The normalized and zero-center word vectors, a KeyedVectors object. 
        - target_terms: A list of target terms, such as ['lesbian', 'gay', 'bisexual', 'transgender']
        - target_forms_dict: A dictionary of words to their morphologically related words.
        
    Returns the cosine similarity between a target vector and a vermin vector.
    '''
    # create vermin weighted average vector 
    vermin_vec = get_weighted_vector(wv, all_vermin_singulars, all_vermin_plurals_dict)
    # create target_term vector
    target_vec = get_weighted_vector(wv, target_terms, target_forms_dict)
    return wv.cosine_similarities(target_vec, [vermin_vec])

def main(argv):
    year = ""
    try:
      opts, args = getopt.getopt(argv,"hy:",["year="])
    except getopt.GetoptError:
        print 'test.py -y <year>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -y <year>'
            sys.exit()
        elif opt in ("-y", "--year"):
            year = arg

    wv_path = "../models/nyt-" + year + ".wordvectors"
    wv = KeyedVectors.load(wv_path) # these should be normalized and centered already

    lexicon = pd.read_csv(LEXICON_PATH, sep='\t')

    # TODO: actually calling the functions for each year

if __name__ == "__main__":
    main(sys.argv[1:])
  

    




