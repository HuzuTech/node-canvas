#!/bin/bash

export PKG_CONFIG_PATH=`pwd`/local/lib/pkgconfig

./install `pwd`/local
node-waf configure build

