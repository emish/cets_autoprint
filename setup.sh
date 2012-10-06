#!/usr/bin/sh

cd

# Make the python local library
if ! [ -d lib ]
then
mkdir lib
fi
cd lib
if ! [ -d python]
then
mkdir python
fi

cd

# Setup your pythonpath correctly
echo >> .bashrc
echo 'PYTHONPATH=~/lib/python:$PYTHONPATH' >> .bashrc
easy_install -d ~/lib/python pyPdf

mkdir to_print

git clone https://github.com/emish/cets_autoprint.git autoprint

screen -S autoprint
./autoprint/autoprint.py &
screen -d autoprint
