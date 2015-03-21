# ---- Link --------------------------- 
_C_dtw.so:  C_dtw.o 
	gcc -shared C_dtw.o -o _C_dtw.so  

# ---- gcc C compile ------------------
C_dtw.o:  C_dtw.c C_dtw.h
	gcc  -c C_dtw.c -I/usr/include/python2.7 -I/usr/lib/python2.7/dist-packages/numpy/core/include/numpy
