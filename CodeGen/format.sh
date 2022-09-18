#!/bin/sh

find . \
    -not \( -path "*/templates/*" -prune \) \
    \( -name \*.h -o -name \*.hpp -o -name \*.c -o -name \*.cc -o -name \*.cpp \) \
    | xargs clang-format-10 -style=file -i