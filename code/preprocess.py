import re
import argparse
from pdb import set_trace as bp

def get_data(filename: str, preprocessed=False):
    with open(filename) as f:
        for line in f:
            if not preprocessed:
                line = process_line(line).rstrip()

            yield line.split(' ')


def process_line(line: str):
    return re.sub('[^a-z ]', '', line.strip().lower())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='file to preprocess')
    parser.add_argument('-p', help='flag to indicate data needs preprocessing', default=False, action='store_true')
    
    args = parser.parse_args()

    for paragraph in get_data(args.filename, args.p):
        print(paragraph)

# get_data('../data/nyt-paras.tsv')

