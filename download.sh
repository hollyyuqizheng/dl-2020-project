mkdir data
cd data
wget -nc https://www.dropbox.com/s/6urc128kepdhovr/nyt-paras.tsv

python3 ../code/nyt_process.py
