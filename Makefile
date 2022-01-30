### Top-level Makefile 
# Used to organize analysis
# target variable to create all elements in Makefile
all: merged analyze final

# target names that are not specific files, but are are reference names
.PHONY: all merged analyzed final
# has no depedencies
.SECONDARY: install clean

# clean & merge data
merged: ./python/merge_adni.py ./data/DTIROI_04_30_14-1.csv ./data/GDSCALE-4.csv
	python $(word 1,$^)

# install required packages
install:
	# pip is used to install rpy2, which is necessary to run gam.py
	# pip is a package manager for python 
	# if pip is not installed on your laptop, follow the instructions on this website: https://pip.pypa.io/en/stable/installing/
	# you may also have to use Homebrew to install: brew install llvm # clang/llvm
	# and: brew install libomp #OpenMP support
	CC=/usr/local/Cellar/llvm/7.0.1/bin/clang pip install rpy2==2.7.9 --user
	#CC=/usr/local/Cellar/llvm/7.0.1/bin/clang pip install rpy2 --upgrade
	pip install singledispatch

# analyze data using generalized additive model
analyzed: merged ./python/gam.py
	# first, type “make install” to use pip (a python package manager) to install rpy2
	python $(word 2,$^)
	echo

# clean
clean:
	rm ./data/merged.csv
	rm -rf ./results/*

