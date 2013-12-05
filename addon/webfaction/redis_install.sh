#!/bin/sh

cd $HOME/src
wget http://redis.googlecode.com/files/redis-2.6.14.tar.gz
cd redis-2.6.14
make \
PREFIX=$HOME BINDIR=$HOME/bin \
INCLUDEDIR=$HOME/include LIBDIR=$HOME/lib \
DATADIR=$HOME/share MANDIR=$HOME/share/man \
install