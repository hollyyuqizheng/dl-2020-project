mkdir data
cd data


# fileid="1rSP8ZOp_gq7lRifsq73KXZXvq_CTtvkT" - this is an old id
fileid="1y_S5Je86csU-vfcoNUBob3S-sSKijBen"
filename="nyt-data.tar.gz"
cookie_file=".cookie"

if [[ ! -f $filename ]]
then
	# get the file, save the cookies cuz apparently that is necessary
	wget --save-cookies $cookie_file "https://drive.google.com/uc?export=download&id=$fileid" -O /dev/null
	code="$(awk '/_warning_/ {print $NF}' $cookie_file)"
	wget --load-cookies $cookie_file "https://drive.google.com/uc?export=download&confirm=$code&id=$fileid" -O $filename
	rm $cookie_file
	
	# untar the file
	tar -v -xzf $filename
else
	echo "$filename already downloaded"
fi
