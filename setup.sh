#!/usr/bin/sh

cd

mkdir to_print

git clone https://github.com/emish/cets_autoprint.git autoprint

python autoprint/autoprint.py &

echo "Your to_print directory is now automated. Thanks for playing."

screen -d
