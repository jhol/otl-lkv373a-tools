#!/bin/bash

set -x
set -u
set -e

prefix=$(pwd)/_prefix

export PATH=${prefix}/bin:${PATH} 

#
# Download
#

binutils_version=2.32
binutils_file_name=binutils-${binutils_version}
binutils_file=${binutils_file_name}.tar.xz
[ -f $binutils_file ] || wget https://mirror.koddos.net/gnu/binutils/${binutils_file}

gcc_version=9.2.0
gcc_file_name=gcc-${gcc_version}
gcc_file=${gcc_file_name}.tar.xz
[ -f ${gcc_file} ] || \
  wget ftp://ftp.mirrorservice.org/sites/sourceware.org/pub/gcc/releases/gcc-${gcc_version}/${gcc_file}

newlib_version=3.1.0
newlib_file_name=newlib-${newlib_version}
newlib_file=${newlib_file_name}.tar.gz
[ -f ${newlib_file} ] || wget ftp://sourceware.org/pub/newlib/${newlib_file}

#
# Binutils
#

(

tar -xf ${binutils_file}
mkdir -p ${binutils_file_name}/_build
cd ${binutils_file_name}/_build
../configure \
  --target=or1k-elf \
  --prefix=$prefix \
  --disable-nls \
  --enable-multilib
make -j$(nproc)
make install

)

rm -rf ${binutils_file_name}/


#
# GCC Bootstrap
#

(

tar -xf ${gcc_file}
mkdir -p ${gcc_file_name}/_build_bootstrap
cd ${gcc_file_name}/_build_bootstrap
../configure \
  --target=or1k-elf \
  --prefix=$prefix \
  --disable-nls \
  --enable-multilib \
  --enable-languages=c \
  --with-newlib \
  --without-headers \
  --disable-shared
make -j$(nproc) all-gcc
make install-gcc

)

rm -rf ${gcc_file_name}/_build_bootstrap

#
# Newlib
#

(

tar -xf newlib-${newlib_version}.tar.gz
mkdir -p ${newlib_file_name}/_build
cd ${newlib_file_name}/_build
../configure \
  --target=or1k-elf \
  --prefix=$prefix \
  --disable-nls \
  --enable-multilib \
  --disable-newlib-supplied-syscalls
make -j$(nproc)
make install

)

rm -rf ${newlib_file_name}

#
# GCC 
#

(

mkdir -p ${gcc_file_name}/_build
cd ${gcc_file_name}/_build
../configure \
  --target=or1k-elf \
  --prefix=$prefix \
  --disable-nls \
  --enable-multilib \
  --enable-languages=c,c++ \
  --with-newlib \
  --disable-shared
make -j$(nproc) all
make install

)

rm -rf ${gcc_file_name}
