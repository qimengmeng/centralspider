#!/bin/bash

pyver=2.7.6

virname=central-py27

pydir=$1

#install pyenv

git clone https://github.com/yyuu/pyenv.git  /usr/local/pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc

echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc

echo 'eval "$(pyenv init -)"' >> ~/.bashrc

exec $SHELL

source ~/.bashrc

pyenv install $pyver

#install virtualenv

git clone https://github.com/yyuu/pyenv-virtualenv.git  /usr/local/pyenv/plugins/pyenv-virtualenv

echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

source ~/.bashrc

pyenv virtualenv $pyver $virname

#set pydir

cd $pydir


