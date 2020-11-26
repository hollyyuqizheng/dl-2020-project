wget -nc https://www.dropbox.com/s/6urc128kepdhovr/nyt-paras.tsv
python3 ../nyt_process.py 
tar -cvzf nyt-data.tar.gz nyt-data-*