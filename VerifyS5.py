import argparse
import pathlib

header = "import random as rnd\n\n"
header += "def S5(x, y):\n"
body = ""
tail = ""
nshares = 0
l = 0

#Transforms the maskverif file into a python file
with open("S5maskVerif.ml") as file:
    record = False
    phase2 = True
    while line := file.readline():
        if ("x0 := x[0];" in line):
            record = True
        if "end" in line:
            record = False
            tail += "  return(z)\n\n"
        if ("inputs: " in line):
            i = 14
            while (ord(line[i]) - ord('0')>=0) and (ord(line[i]) - ord('0')<10):
                nshares *= 10
                nshares += ord(line[i]) - ord('0')
                i+=1
            nshares += 1
            header += "  z = [0 for _ in range(%d)]\n\n" % nshares
        if phase2:
            if "(* ----------Phase 2---------- *)" in line:
                phase2=False
            for i in range(nshares):
                if ("u%d" % i) in line:
                    if i+2 > l:
                        l = i+2
        if ("randoms: " in line):
            rec = False
            randVariable = ""
            for chr in line.replace(" ",""):
                if rec:
                    if (chr == ',') or (chr == ';'):
                        header += "  " + randVariable
                        header += " = rnd.randrange(0,2)\n"
                        randVariable = ""
                    else:
                        randVariable += chr
                if chr == ':':
                    rec = True
            header += "\n\n"
        if record:
            body += line.replace("(*", "#(*").replace(":=","=").replace(";","").replace(" + "," ^ ").replace(" * "," & ")
file.close()

tail += "for i in range(100):\n"
tail += "  x = [rnd.randrange(0,2) for _ in range(%d)]\n" % (nshares)
tail += "  y = [rnd.randrange(0,2) for _ in range(%d)]\n\n" % (nshares)
tail += "  z = S5(x,y)\n\n"
tail += "  X = 0\n"
tail += "  Y = 0\n"
tail += "  Z = 0\n"
tail += "  for j in range(%d):\n" % (l)
tail += "    X ^= x[j]\n"
tail += "    Y ^= y[j]\n"
tail += "    Z ^= z[j]\n"
tail += "  assert(X&Y == Z)\n\n\n"
tail += "print(\"S5 AND gadget computes x&y correctly for 100 random inputs\")\n"
tail += "print(\"Number of XORs: %d\")\n" % body.count('^')
tail += "print(\"Number of ANDs: %d\")" % body.count('&')

print(header+body+tail)
