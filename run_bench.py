import pstats

#p = pstats.Stats('output.pstats')
p = pstats.Stats('run11302392616.19')

p.sort_stats('cumulative').print_stats(10)

#python gprof2dot.py -f pstats run11301293498.59 | dot -Tpng -o output.png