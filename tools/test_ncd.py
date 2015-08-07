import bz2, zlib

def normalized_compression_distance(action_sequence, other_action_sequence, algorithm):
    """
    More details in: 
        Gomez, Faustino J. "Sustaining diversity using behavioral information distance." Proceedings of the 
        11th Annual conference on Genetic and evolutionary computation. ACM, 2009.
    """
    # action_sequence = [str(a) for a in action_sequence]
    # other_action_sequence = [str(a) for a in other_action_sequence]
    x_len = len(algorithm.compress("".join(action_sequence)))
    y_len = len(algorithm.compress("".join(other_action_sequence)))
    xy_len = len(algorithm.compress("".join(action_sequence+other_action_sequence)))
    distance = (xy_len - min(x_len, y_len))/float(max(x_len, y_len))
    # if distance < 0.0:
    #     # print "Warning! Value lower than 0.0 for NCD! Value: "+str(distance)+" ("+str(x_len)+","+str(y_len)+","+str(xy_len)+")"
    #     distance = 0.0
    # if distance > 1.0:
    #     # print "Warning! Value higher than 1.0 for NCD! Value: "+str(distance)+" ("+str(x_len)+","+str(y_len)+","+str(xy_len)+")"
    #     distance = 1.0
    return distance

def b(x):
    return (x - 0.04)/(0.285714285714-0.04)

def z(x):
    return (x - 0.0869565217391)/(0.68-0.0869565217391)

if __name__ == "__main__":
    """
    Compare bzip and zip across test cases (always fold x always fold, 
    always raise x always raise, always fold x always raise, smart x always fold, 
    smart x always raise)
    """
    # 15 hands against random opponents
    folds = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    raises = ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
    calls = ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
    raises_2 = ['2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
    fr = ['0', '0', '0', '0', '0', '0', '0', '0', '2', '2', '0', '2', '2', '2', '2', '0']
    fr_2 = ['0', '0', '0', '0', '0', '0', '0', '2', '2', '0', '0', '2', '2', '0', '0']
    fc = ['0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '0', '1', '1', '1', '1', '0', '1', '1', '0', '1', '1', '1', '0', '0']
    cr = ['2', '2', '1', '1', '2', '1', '1', '1', '2', '1', '2', '1', '2', '2', '2', '1', '2', '2', '2', '1', '1', '1', '2', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '2', '2']
    cr_2 = ['2', '2', '2', '2', '1', '2', '1', '2', '1', '2', '1', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '2', '1', '1', '2', '1', '1', '2', '2', '2', '1', '2', '1', '2', '2', '1', '1', '1', '2']
    fc_2 = ['0', '0', '0', '0', '0', '0', '0', '1', '1', '1', '0', '0', '0', '1', '1', '0', '1', '1', '1', '1', '0', '0']
    fr2 = ['2', '0', '2', '2', '2', '2', '0', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
    fcr = ['2', '0', '2', '2', '1', '1', '0', '2', '2', '1', '2', '2', '1', '1', '2', '2', '2', '2', '2', '1', '1', '2', '2', '2', '2', '2', '2', '2', '2', '1', '1']
    print "--- low distances => better"
    i = [raises, raises_2]
    print "raises x raises_2: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [fr, fr_2]
    print "fr x fr_2: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [cr, cr_2]
    print "cr x cr_2: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [fc, fc_2]
    print "fc x fc_2: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [fcr, fcr]
    print "fcr x fcr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    print "---"
    print "--- high distances => better"
    i = [folds, raises]
    print "folds x raises: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [folds, calls]
    print "folds x calls: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [raises, calls]
    print "raises x calls: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    print "---"
    print "--- high distances => better"
    i = [fr, cr]
    print "fr x cr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [cr, fc]
    print "cr x fc: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [fc, fr]
    print "fc x fr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    print "---"
    print "--- high distances => better"
    i = [folds, cr]
    print "folds x cr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [calls, fr]
    print "calls x fr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [raises, fc]
    print "raises x fc: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    print "---"
    print "--- high distances => better"
    i = [fcr, fr]
    print "fcr x fr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [fcr, fc]
    print "fcr x fc: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [calls, fr2]
    print "calls x fr2: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    i = [fcr, cr]
    print "fcr x cr: "+str(normalized_compression_distance(i[0], i[1], bz2))+" | "+str(normalized_compression_distance(i[0], i[1], zlib))
    print "---"
# ['2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
# ['2', '2', '2', '2', '1', '2', '1', '2', '1', '2', '1', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '2', '1', '1', '2', '1', '1', '2', '2', '2', '1', '2', '1', '2', '2', '1', '1', '1', '2']
# ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
# ['2', '2', '2', '2', '2', '2', '2', '0', '2', '2', '2', '0', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
# ['2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['2', '1', '2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '2', '0', '2', '2', '0']
# ['0', '0', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '1', '1', '0', '1', '1', '1', '0', '0']
# ['1', '2', '1', '2', '1', '2', '2', '1', '1', '1', '2', '2', '1', '2', '1', '2', '2', '2', '1', '1', '2', '1', '1', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '1', '2', '1', '2']
# ['2', '0', '2', '2', '2', '2', '0', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['2', '1', '2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['2', '1', '2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['1', '2', '1', '2', '1', '2', '2', '1', '1', '1', '2', '2', '1', '2', '1', '2', '2', '2', '1', '1', '2', '1', '1', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '1', '2', '1', '2', '2', '2', '2', '1', '2', '1', '2']
# ['0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '2', '0', '2', '2', '0']
# ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
# ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']
# ['0', '0', '0', '0', '0', '1', '1', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '0']
# ['0', '0', '0', '0', '0', '1', '1', '1', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '0']

"""
bz2: min = 0.04, max = 0.285714285714
zlib: min = 0.0869565217391, max = 0.68
stephen == bz2
stephen/1.2

--- low distances => better
raises x raises_2: 0.130434782609 | 0.2 | 0.130435 | 0.108696
fr x fr_2: 0.0909090909091 | 0.3125 | 0.0909091 | 0.0757576
cr x cr_2: 0.156862745098 | 0.44 | 0.156863 | 0.130719
fc x fc_2: 0.108695652174 | 0.35 | 0.108696 | 0.0905797
fcr x fcr: 0.04 | 0.0869565217391 | 0 | 0
---
--- high distances => better
folds x raises: 0.153846153846 | 0.25 | 0.153846 | 0.128205
folds x calls: 0.153846153846 | 0.25 | 0.153846 | 0.128205
raises x calls: 0.153846153846 | 0.166666666667 | 0.153846 | 0.128205
---
--- high distances => better
fr x cr: 0.224489795918 | 0.6 | 0.22449 | 0.187075
cr x fc: 0.224489795918 | 0.64 | 0.22449 | 0.187075
fc x fr: 0.108695652174 | 0.5 | 0.108696 | 0.0905797
---
--- high distances => better
folds x cr: 0.285714285714 | 0.68 | 0.285714 | 0.238095
calls x fr: 0.227272727273 | 0.4375 | 0.227273 | 0.189394
raises x fc: 0.239130434783 | 0.55 | 0.23913 | 0.199275
---
--- high distances => better
fcr x fr: 0.18 | 0.652173913043 | 0.18 | 0.15
fcr x fc: 0.22 | 0.608695652174 | 0.22 | 0.183333
calls x fr2: 0.239130434783 | 0.4375 | 0.23913 | 0.199275
---

I used as inputs patterns of action sequences of SBB teams in 15 hands 
against a random opponent. The results are normalized between the min 
and max value so they can be better compared.

Glossary: For example, fr_1 is a sequence of folds (f) and raises (r), and 
fr_2 is another sequence with a similar pattern of folds and raises, but in 
a different order.

--- Tests were small distances are expected (comparison: bz2 | gzip):
fr x fr_2: 0.207188160677 | 0.380315249267
cr x cr_2: 0.475604195167 | 0.595307917889
fc x fc_2: 0.279575328615 | 0.443548387097
fcr x fcr: 0.0 | 0.0
Conclusion: For all besides the last one, gzip performed poorly, and bz2
performed poorly for cr x cr_2

--- Tests were big distances are expected (comparison: bz2 | gzip):
folds x raises: 0.463327370305 | 0.274926686217
folds x calls: 0.463327370305 | 0.274926686217
raises x calls: 0.463327370305 | 0.134408602151
fr x cr: 0.750830564785 | 0.865102639296
cr x fc: 0.750830564785 | 0.932551319648
fc x fr: 0.279575328615 | 0.696480938416
folds x cr: 1.0 | 1.0 
calls x fr: 0.762156448204 | 0.591092375367
raises x fc: 0.810414560163 | 0.780791788856
fcr x fr: 0.569767441861 | 0.953079178886
fcr x fc: 0.732558139536 | 0.879765395894
calls x fr2: 0.810414560163 | 0.591092375367
fcr x cr: 0.651162790698 | 0.730205278592
Conclusion: The first three comparisons performed very poorly for both 
algorithms. The other results make more sense, but there isn't a clear 
relationship for why some were bigger than others.

"""

"""
folds = '00000000000000000'
raises = '22222222222222222222222222222222222222222222222222222222222222222222'
calls = '1111111111111111111111111111111111111111111111111111111111111111'
raises_2 = '2222122222222222222222222'
fr = '0000000022022220'
fr_2 = '000000022002200'
fc = '000000001101111011011100'
cr = '22112111212122212221112222121222222'
cr_2 = '222212121212221212222211211222121221112'
fc_2 = '0000000111000110111100'
fr2 = '2022220222222222222222222222222'
fcr = '2022110221221122222112222222211'
"""

"""
--- low distances => better
raises x raises_2: 0.368048533873 | 0.190615835777 zlib
fr x fr_2: 0.207188160677 | 0.380315249267 bz2
cr x cr_2: 0.475604195167 | 0.595307917889 bz2
fc x fc_2: 0.279575328615 | 0.443548387097 bz2
fcr x fcr: 0.0 | 5.13183093283e-14 ==
---
--- high distances => better
folds x raises: 0.463327370305 | 0.274926686217 bz2
folds x calls: 0.463327370305 | 0.274926686217 bz2
raises x calls: 0.463327370305 | 0.134408602151 bz2
---
--- high distances => better
fr x cr: 0.750830564785 | 0.865102639296
cr x fc: 0.750830564785 | 0.932551319648
fc x fr: 0.279575328615 | 0.696480938416
---
--- high distances => better
folds x cr: 1.0 | 1.0 == 
calls x fr: 0.762156448204 | 0.591092375367 bz2
raises x fc: 0.810414560163 | 0.780791788856 ==
---
--- high distances => better
fcr x fr: 0.569767441861 | 0.953079178886 zlib
fcr x fc: 0.732558139536 | 0.879765395894 zlib
calls x fr2: 0.810414560163 | 0.591092375367 bz2
---
"""