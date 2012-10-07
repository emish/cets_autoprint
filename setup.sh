#!/usr/bin/sh

cd

mkdir to_print

git clone https://github.com/emish/cets_autoprint.git autoprint

screen -S autoprint
python autoprint/autoprint.py &
screen -d autoprint
