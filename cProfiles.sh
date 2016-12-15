#!/bin/bash

python -m cProfile -o /tmp/test.out ../test.py
gprof2dot -f pstats /tmp/test.out  | dot -Tpng -o test.png
