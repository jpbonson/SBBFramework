CC = gcc
CFLAGS = -O3 -Wall

PROGRAMS = all_in_expectation bm_run_matches dealer example_player

all: $(PROGRAMS)

clean:
	rm -f $(PROGRAMS)


all_in_expectation: all_in_expectation.c game.c game.h rng.c rng.h net.c net.h
	$(CC) $(CFLAGS) -o $@ all_in_expectation.c game.c rng.c net.c

bm_server: bm_server.c game.c game.h rng.c rng.h net.c net.h
	$(CC) $(CFLAGS) -o $@ bm_server.c game.c rng.c net.c

bm_widget: bm_widget.c net.c net.h
	$(CC) $(CFLAGS) -o $@ bm_widget.c net.c

bm_run_matches: bm_run_matches.c net.c net.h
	$(CC) $(CFLAGS) -o $@ bm_run_matches.c net.c

dealer: game.c game.h evalHandTables rng.c rng.h dealer.c net.c net.h
	$(CC) $(CFLAGS) -o $@ game.c rng.c dealer.c net.c

example_player: game.c game.h evalHandTables rng.c rng.h example_player.c net.c net.h
	$(CC) $(CFLAGS) -o $@ game.c rng.c example_player.c net.c

# http://www.swig.org/Doc1.3/Python.html
# https://studywolf.wordpress.com/2013/05/21/cython-journey-part-3-wrapping-c-code-and-passing-arrays/

# swig -python dealer.i
# gcc -c -fPIC game.c rng.c dealer.c net.c dealer_wrap.c -I/usr/include/python2.7 -I/usr/include/tcl8.4
# ld -shared game.o rng.o dealer.o net.o dealer_wrap.o -o _dealer.so

# rm game.o rng.o dealer.o net.o dealer_wrap.o _dealer.so

# import dealer
# dealer.main(6, ['matchName', 'holdem.limit.2p.reverse_blinds.game', '1000', '0', 'Alice', 'Bob'])

# gcc -c -fPIC game.c rng.c dealer.c net.c
# ld -shared game.o rng.o dealer.o net.o -o dealer.so

# import numpy as np
# import ctypes
# dealer = ctypes.cdll.LoadLibrary("./dealer.so")
# myargv = ctypes.c_char_p*7
# argv = myargv('dealer', 'matchName', 'holdem.limit.2p.reverse_blinds.game', '1000', '0', 'Alice', 'Bob')
# Argv = ctypes.pointer ( argv )
# dealer.main(7, Argv)

# swig -python argv.i
# gcc -c -fPIC argv_wrap.c -I/usr/include/python2.7 -I/usr/include/tcl8.4
# ld -shared argv_wrap.o -o _argv.so 