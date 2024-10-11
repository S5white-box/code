from circkit.boolean import OptBooleanCircuit as BooleanCircuit
from binteger import Bin
import sys
from wboxkit.prng import NFSR, Pool
from wboxkit.ciphers.aes import BitAES
from wboxkit.serialize import RawSerializer
from S5 import S5
import os
import argparse

key = b"abcdefghABCDEFGH"


def createS5(l,s,r):
    #The Pseudo-Random Number Generator used to create fresh randomness in the circuit
    nfsr = NFSR(
        taps=[[], [11], [50], [3, 107]],
        clocks_initial=100,
        clocks_per_step=1,
    )
    prng = Pool(prng=nfsr, n=256)


    #Creating a simple AES circuit
    C = BooleanCircuit(name="AES")
    pt = C.add_inputs(128)
    ct, k2 = BitAES(pt, Bin(key).tuple, rounds=r)
    C.add_output(ct)
    C.in_place_remove_unused_nodes()


    #Applying S5 to the base AES circuit
    C_S5 = S5(prng=prng, order=l, dummy=s).transform(C)
    C_S5.in_place_remove_unused_nodes()


    #Verifying that the protected implementation returns the same output
    for i in range(10):
        plaintext = os.urandom(16)
        ct1 = C.evaluate(Bin(plaintext).tuple)
        ct2 = C_S5.evaluate(Bin(plaintext).tuple)
        assert ct1==ct2


    #Saving the output circuit to a file, which can be used with wboxkit to generate traces
    RawSerializer().serialize_to_file(C_S5, "circuits/aes%d_S5_%d_%d.bin" % (r,l,s))


    #Printing circuit stats of the base AES and its protected version
    print("Regular AES stats:")
    C.print_stats()

    print("\nS5 AES stats:")
    C_S5.print_stats()


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

    createS5(args.linear_shares, args.slots, args.rounds)
