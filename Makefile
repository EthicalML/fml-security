
build-readme:
	jupyter nbconvert --to markdown README.ipynb
	jupyter nbconvert --to markdown SETUP.ipynb
