import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from preprocess import get_data
from pathlib import Path
from words import all_vermin_singulars, all_vermin_plurals_dict, all_target_singulars, all_target_plurals_dict, all_moral_disgust_stem, all_moral_disgust_dict, target_american, target_american_plural, target_homosexual, target_homosexual_plural, target_gay, target_gay_plural
import pandas as pd
import sys, getopt
import csv

from pdb import set_trace as bp

# --------------- Parameters  -----------------
LEXICON_PATH = '../data/NRC-VAD-Lexicon.txt'
COUNT_PARAM_NAME = 'count'
TARGET_LIST = target_american
TARGET_PLURAL_DICT = target_american_plural
CSV_NAME = ""

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
    similar_words = [item[0] for item in wv.similar_by_vector(target_vec, topn=n)]

    similar_words_lexicon = lexicon[lexicon['Word'].isin(similar_words)]

    count = []
    for word in similar_words_lexicon.Word:
        try:
            count.append(wv.get_vecattr(word, COUNT_PARAM_NAME))
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
    similar_words = [item[0] for item in wv.similar_by_vector(target_vec, topn=n)]

    similar_words_lexicon = lexicon[lexicon['Word'].isin(similar_words)]

    count = []
    for word in similar_words_lexicon.Word:
        try:
            count.append(wv.get_vecattr(word, COUNT_PARAM_NAME))
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
    return wv.cosine_similarities(target_vec, [moral_disgust_vec])[0]

# Section 3.4 -- Vermin as a Dehumanizing Metaphor 
def vermin(wv, target_terms, target_forms_dict):
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
    return wv.cosine_similarities(target_vec, [vermin_vec])[0]

def main(argv):
    year = ""
    word = ""

    try:
      opts, args = getopt.getopt(argv,"hy:w",["year=", "word="])
    except getopt.GetoptError:
        print('test.py -y <year>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('test.py -y <year>')
            sys.exit()
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-w", "--word"):
            word = arg

    lexicon = pd.read_csv(LEXICON_PATH, sep='\t')

    if word == "american":
        TARGET_LIST = target_american
        TARGET_PLURAL_DICT = target_american_plural
        CSV_NAME = "american"
    elif word == "homosexual":
        TARGET_LIST = target_homosexual
        TARGET_PLURAL_DICT = target_homosexual_plural
        CSV_NAME = "homosexual"
    elif word == "gay":
        TARGET_LIST = target_gay
        TARGET_PLURAL_DICT = target_gay_plural
        CSV_NAME = "gay"
    else:
        print("error in reading word")

    if year == "all":
        csv_out_file = "../analysis/scores_by_year_" + CSV_NAME + ".csv"
        with open(csv_out_file, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['year', 'negative_eval', 'denial_agency', 'moral_disgust', 'vermin'])

            for y in range(1986, 2017):
                wv_path = "../models/year_" + str(y) + "/nyt_" + str(y) + ".model"
                wv = Word2Vec.load(wv_path).wv # these should be normalized and centered already

                negative_eval_score = negative_evaluation(wv, TARGET_LIST, lexicon, TARGET_PLURAL_DICT)
                denial_agency_score = denial_of_agency(wv, TARGET_LIST, lexicon, TARGET_PLURAL_DICT)
                moral_disgust_score = moral_disgust(wv, TARGET_LIST, TARGET_PLURAL_DICT)
                vermin_score = vermin(wv, TARGET_LIST, TARGET_PLURAL_DICT)

                # print(negative_eval_score)
                # print(denial_agency_score)
                # print(moral_disgust_score)
                # print(vermin_score)

                row_to_write = [y, negative_eval_score, denial_agency_score, moral_disgust_score, vermin_score]
                writer.writerow(row_to_write)
    else:
        print("tbd..")

if __name__ == "__main__":
    main(sys.argv[1:])
  

    




