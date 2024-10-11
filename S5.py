from functools import reduce
from operator import xor
from queue import PriorityQueue

import logging

from circkit.transformers.core import CircuitTransformer
from circkit.array import Array

from wboxkit.containers import Rect

from wboxkit.masking import MaskingTransformer

log = logging.getLogger(__name__)

def xorlist(lst):
    return reduce(xor, lst, 0)



class S5(MaskingTransformer):
        NAME_SUFFIX = "_S5"
        EPSILON = 1e-9

        def __init__(self, *args, order=2, dummy=2, max_bias=1/8.0, **kwargs):
            self.slots = int(dummy)      # equals to s in the paper
            self.lin_shares = int(order) # equals to l in the paper
            n_shares = int(self.slots + self.lin_shares - 1)
            super().__init__(*args, n_shares=n_shares, **kwargs)

            self.max_bias = float(max_bias)
            assert 0 < self.max_bias <= 1

            self.refresh = None
            self.initialized = 0


        #Creates the flags
        def create_shuffle(self, n_slots):
            flags = []

            cur_ver = {i: 0 for i in range(n_slots)}

            # -prob, index, version
            pq_max = PriorityQueue()
            pq_max.put((-1.0, 0, 0))

            #-prob, index, version
            pq_min = PriorityQueue()
            for i in range(1, n_slots):
                pq_min.put((0.0, i, 0))

            goal = 1 / n_slots
            ubound = goal + self.max_bias
            lbound = goal - self.max_bias
            while True:
                assert not pq_max.empty()
                src_prob, src, src_ver = pq_max.get()
                src_prob = -src_prob
                if src_ver != cur_ver[src]:
                    continue

                found = 0
                while not pq_min.empty():
                    dst_prob, dst, dst_ver = pq_min.get()
                    #print("try", dst, dst_prob)
                    if dst_ver != cur_ver[dst]:
                        continue
                    if src == dst:
                        continue
                    if abs(src_prob - dst_prob) < self.EPSILON:
                        continue

                    found = 1
                    break

                if (lbound <= dst_prob + self.EPSILON
                    and src_prob <= ubound + self.EPSILON):
                    log.info(
                        "finished with probs"
                        f" lb:{lbound:.3f}"
                        f" <= min:{dst_prob:.3f}"
                        f" <= goal:{goal:.3f}"
                        f" <= max:{src_prob:.3f}"
                        f" <= ub:{ubound:.3f}"
                    )
                    break

                assert found

                prob = (src_prob + dst_prob) / 2
                log.info(f"swap {src} {dst}: {src_prob:.3f} {dst_prob:.3f} -> {prob:.3f}")

                flag = self.rand()
                flags.append((flag, src, dst))

                ver = max(src_ver, dst_ver) + 1

                cur_ver[src] = ver
                cur_ver[dst] = ver

                pq_max.put((-prob, src, ver))
                pq_max.put((-prob, dst, ver))

                pq_min.put((prob, src, ver))
                pq_min.put((prob, dst, ver))
            return flags

        #The Dummy Shuffling suhuffle function
        def shuffle(self, xs, flags):
            xs = list(xs)
            for flag, i, j in flags:
                xs[i], xs[j] = self.cswap(xs[i], xs[j], flag)
            return xs

        #The Dummy SHuffling unshuffle function
        def unshuffle(self, xs, flags):
            xs = list(xs)
            for flag, i, j in reversed(flags):
                xs[i], xs[j] = self.cswap(xs[i], xs[j], flag)
            return xs

        def cswap(self, x, y, flag):
            dxy = flag & (x ^ y)
            return (dxy ^ y, dxy ^ x)

        #Algorithm 5 of the paper
        def refreshSlots(self, x):
            rand = [self.rand() for _ in range(self.slots-1)]
            rand.insert(0,0)
            rand = self.shuffle(rand, flags=self.flags)
            for i in range(self.slots):
                x[i + self.lin_shares - 1] = x[i + self.lin_shares - 1] ^ rand[i]
            return(x)

        #Algorithm 6 of the paper
        def SharedShuffledRandomness(self):
            shufRand = [self.rand() for _ in range(self.slots-1)]
            shufRand.insert(0,0)
            shufRand = self.shuffle(shufRand, flags=self.flags)

            #SNI sharing shuffled randomnes (Gadget 4b from "Strong Non-Interference and Type-Directed Higher-Order Masking")
            srnd = [[0] * (self.lin_shares-2) for _ in range(self.slots)]
            for s in range(self.slots):
                srnd[s].append(shufRand[s])

            for s in range(self.slots):
                for i in range(self.lin_shares-1):
                    for j in range(i+1, self.lin_shares-1):
                        r = self.rand()
                        srnd[s][i] = srnd[s][i] ^ r
                        srnd[s][j] = srnd[s][j] ^ r

            return(srnd)

        #Algorithm 3 of the paper
        def encode(self, s):
            if not self.initialized:
                self.flags = self.create_shuffle(self.slots)
                self.initialized = 1
            x = [self.rand() for _ in range(self.lin_shares-1)]
            dummies = [self.rand() for _ in range(self.slots-1)]
            dummies.insert(0, xorlist(x) ^ s)
            dummies = self.shuffle(dummies, flags=self.flags)
            return Array(x+dummies)

        def decode(self, x):
            linearPart = x[:self.lin_shares-1]
            dummies = x[-self.slots:]
            dummies = self.unshuffle(dummies, flags=self.flags)
            return xorlist(linearPart) ^ dummies[0]

        def visit_XOR(self, node, x, y):
            return x ^ y

        #Algorithm 4 of the paper
        def visit_AND(self, node, x, y):
            x = self.refreshSlots(x)
            y = self.refreshSlots(y)

            r = [[0] * self.lin_shares for _ in range(self.n_shares)]

            #Step 1
            for i in range(self.lin_shares-1):
                for j in range(i+1, self.lin_shares-1):
                    r[i][j] = self.rand()
                    r[j][i] = ( r[i][j] ^ x[i]&y[j] ) ^ x[j]&y[i]

            #Step 2
            for i in range(self.lin_shares-1):
                r[i][self.lin_shares-1] = self.rand()

            for s in range(self.lin_shares-1, self.n_shares):
                for i in range(self.lin_shares-1):
                    r[s][i] = ( r[i][self.lin_shares-1] ^ x[i]&y[s] ) ^ x[s]&y[i]

            z = x & y  #Also computes the "and" at the end of step 1

            #Step 3
            for i in range(self.lin_shares-1):
                for j in range(self.lin_shares):
                    if i != j:
                        z[i] = z[i] ^ r[i][j]

            #Step 4
            srnd = self.SharedShuffledRandomness()
            for i in range(self.lin_shares-1, self.n_shares):
                for j in range(self.lin_shares-1):
                    z[i] = (z[i] ^ srnd[i-self.lin_shares+1][j]) ^ r[i][j]
            return z

        def visit_NOT(self, node, x):
            x = Array(x)
            x[0] = 1^x[0]
            return x
