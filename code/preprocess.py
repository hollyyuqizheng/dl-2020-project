import re
import argparse

def get_data(filenames: list, preprocessed=False):
    if type(filenames) is not list:
        filenames = [filenames]

    for filename in filenames:
        with open(filename) as f:
            for line in f:
                if not preprocessed:
                    line = process_line(line)
                
                if line:
                    yield line.split()


def process_line(line: str):
    return re.sub('[^a-z ]', '', line.strip().lower())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', help='files to preprocess', nargs='+')
    parser.add_argument('-p', help='flag to indicate data needs preprocessing', default=False, action='store_true')
    
    args = parser.parse_args()

    for paragraph in get_data(args.filenames, preprocessed=args.p):
        print(paragraph)

# get_data('../data/nyt-paras.tsv')

