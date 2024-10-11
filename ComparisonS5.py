from circkit.boolean import OptBooleanCircuit as BooleanCircuit
#import wboxkit
from binteger import Bin
import sys
from wboxkit.prng import NFSR, Pool
from wboxkit.ciphers.aes import BitAES
from wboxkit.serialize import RawSerializer
from wboxkit.masking import ISW, DumShuf
from S5 import S5
import os
import argparse

def CompareS5(l,s,r):
    #Pseudo-Random Number Generator used inside the circuits to generate fresh randomness
    nfsr = NFSR(
        taps=[[], [11], [50], [3, 107]],
        clocks_initial=100,
        clocks_per_step=1,
    )
    prng = Pool(prng=nfsr, n=256)

    #Creating the base AES circuit
    C = BooleanCircuit(name="AES")

    key = b"abcdefghABCDEFGH"

    pt = C.add_inputs(128)
    ct, k2 = BitAES(pt, Bin(key).tuple, rounds=r)
    C.add_output(ct)
    C.in_place_remove_unused_nodes()
    AESnodes = len(C) #Number of nodes of the base circuit

    # print("\nOriginal AES stats:")
    # C.print_stats()
    # print("")

    print("   -----  Stats for l=%d and s=%d  -----   " % (l,s))

    #Computing S5 stats
    C_S5 = S5(prng=prng, order=l, dummy=s).transform(C)
    C_S5.in_place_remove_unused_nodes()

    for i in range(10): #Verification that the protected circuit is correct
        plaintext = os.urandom(16)
        ct1 = C.evaluate(Bin(plaintext).tuple)
        ct2 = C_S5.evaluate(Bin(plaintext).tuple)
        assert ct1==ct2

    print("\nS5_%d_%d AES stats:" % (l,s))
    C_S5.print_stats()
    print("%f times more than the original AES" % (len(C_S5)/AESnodes))

    #Computing ISWoDS stats
    C_ISWoDS = DumShuf(prng=prng, n_shares=s).transform(C)
    C_ISWoDS.in_place_remove_unused_nodes()
    C_ISWoDS = ISW(prng=prng, order=l).transform(C_ISWoDS)
    C_ISWoDS.in_place_remove_unused_nodes()

    for i in range(10): #Verification that the protected circuit is correct
        plaintext = os.urandom(16)
        ct1 = C.evaluate(Bin(plaintext).tuple)
        ct2 = C_ISWoDS.evaluate(Bin(plaintext).tuple)
        assert ct1==ct2

    print("\nISW%doDS%d AES stats:" % (l,s))
    C_ISWoDS.print_stats()
    print("%f times more than the original AES" % (len(C_ISWoDS)/AESnodes))


    #Computing DSoISW stats
    C_DSoISW = ISW(prng=prng, order=l).transform(C)
    C_DSoISW.in_place_remove_unused_nodes()
    C_DSoISW = DumShuf(prng=prng, n_shares=s).transform(C_DSoISW)
    C_DSoISW.in_place_remove_unused_nodes()

    for i in range(10): #Verification that the protected circuit is correct
        plaintext = os.urandom(16)
        ct1 = C.evaluate(Bin(plaintext).tuple)
        ct2 = C_DSoISW.evaluate(Bin(plaintext).tuple)
        assert ct1==ct2

    print("\nDS%doISW%d AES stats:" % (s,l))
    C_DSoISW.print_stats()
    print("%f times more than the original AES" % (len(C_DSoISW)/AESnodes))


if __name__ == '__main__' and '__file__' in globals():
    parser = argparse.ArgumentParser(
        description='description to do later',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-l', '--linear-shares', type=int, default=3,
        help="Number of linear shares"
    )

    parser.add_argument(
        '-s', '--slots', type=int, default=3,
        help="Number of slots"
    )

    parser.add_argument(
        '-r', '--rounds', type=int, default=10,
        help="Number of rounds of the protected AES"
    )

    args = parser.parse_args()

    CompareS5(args.linear_shares, args.slots, args.rounds)
