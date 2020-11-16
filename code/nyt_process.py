from datetime import datetime
from pathlib import Path
import argparse

def create_files(data_path, nyt_data, force=False):
    with open(nyt_data) as f:
        write_dict = {}
        for line in f:
            line_split = line.strip().split('\t')
            # print(line)
            try:
                if len(line_split) == 6:
                    time_index, paragraph_index = 3, 5
                elif len(line_split) == 5:
                    time_index, paragraph_index = 2, 4
                
                time = datetime.strptime(line_split[time_index], '%Y-%m-%dT%H:%M:%SZ')
                year = time.year 
                paragraph = line_split[paragraph_index]
            except Exception as e:
                # print('ERROR:', e)
                # print('line processing failed for:', line)
                # print('line format error, continuing...')
                continue

            if year not in write_dict:
                filename = data_file / 'nyt-data-{}.txt'.format(year)
                if not force and filename.is_file():
                    print(filename, 'already exists! exiting...')
                    exit(0)
                print('creating:', filename)
                f = open(filename, 'w')
                write_dict[year] = f

            write_dict[year].write(re.sub('[^a-z]+', '', paragraph.lower()))
            write_dict[year].write('\n')

            
        for year in write_dict:
            write_dict[year].close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='force the model to overwrite files', action='store_true', default=False)

    args = parser.parse_args()

    data_file = Path('../data')
    filename = data_file / 'nyt-paras.tsv'
    create_files(data_file, filename, args.f)

