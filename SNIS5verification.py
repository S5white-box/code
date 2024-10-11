import argparse

def generateMaskVerifS5(l, s):

    output = ""
    output += "(* tSNI verification of S5_%d_%d using MaskVerif tool *)\n\n" %(l,s)

    output += "proc S5_%d_%d_AND:\n" % (l,s)
    output += "  inputs: x[0:%d], y[0:%d]\n" % (l+s-2, l+s-2)

    output += "  outputs: z[0:%d]\n" % (l+s-2)

    output += "  randoms: "
    # Handling randoms of input / output refresh
    for i in range(1,s):
        output += "refX_%d, " % (i+l-1)
    for i in range(1,s):
            output += "refY_%d, " % (i+l-1)
    for i in range(1,s):
        output += "refZ_%d, " % (i+l-1)

    for line in range(l):
        output += "v%d, " % (line)


    # Handling shuffled random to refresh dummy slots at step 2
    for line in range(l, l+s-1):
        for column in range(l-1):
            output += "srnd%d_%d, " % (line, column)

    for line in range(l-3):
        for column in range(line+1,l-1):
            if (line >= 0) and (column >= 0):
                output += "r%d_%d, " % (line,column)
    if l-3 >= 0:
        output += "r%d_%d;\n" % (l-3,l-2)
    else:
        tmp = list(output)
        tmp[-2] = ';'
        output = "".join(tmp)

    output += "\n  (* ----------Refreshing Inputs---------- *)\n\n" #######################################

    for line in range(l):
        output += "  x%d := x[%d];\n" % (line, line)
    for line in range(l,s+l-1):
        output += "  x%d := x[%d] + refX_%d;\n" % (line, line, line)

    output += "\n"

    for line in range(l):
        output += "  y%d := y[%d];\n" % (line, line)
    for line in range(l,s+l-1):
        output += "  y%d := y[%d] + refY_%d;\n" % (line, line, line)

    output += "\n  (* ----------Phase 1---------- *)\n" #######################################

    for line in range(1,l-1):
        output += "\n  (* line %d *)\n" % line
        for column in range(line):
            output += "  t1_%d_%d := x%d * y%d;\n" % (line,column, line, column)
            output += "  t2_%d_%d := t1_%d_%d + r%d_%d;\n" % (line,column, line,column, column,line)
            output += "  t3_%d_%d := x%d * y%d;\n" % (line,column, column, line)
            output += "  t4_%d_%d := t3_%d_%d + t2_%d_%d;\n\n" % (line,column, line,column, line,column)

    for i in range(l-1):
        output += "  u%d := x%d * y%d;\n" % (i, i, i)

    output += "\n  (* ----------Phase 2---------- *)\n\n" #######################################

    for line in range(l-1,l-1+s):
        output += "  (* line %d *)\n" % line
        for column in range(l-1):
            output += "  w%d_%d_%d := x%d * y%d;\n" % (1,line,column, column, line)
            output += "  w%d_%d_%d := w%d_%d_%d + v%d;\n" % (2,line,column, 1,line,column, column)
            output += "  w%d_%d_%d := x%d * y%d;\n" % (3,line,column, line, column)
            output += "  w%d_%d_%d := w%d_%d_%d + w%d_%d_%d;\n\n" % (4,line,column, 3,line,column, 2,line,column)
        output += "\n"

    for line in range(s):
        output += "  u%d := x%d * y%d;\n" % (line+l-1, line+l-1, line+l-1)

    output += "\n  (* ----------Phase 3---------- *)\n\n" #######################################

    for line in range(l):
        output += "  z0_%d := v%d + u%d;\n" % (line, line, line)
    output += "\n"

    for line in range(l-1):
        output += "\n  (* line %d *)\n" % line
        for column in range(line):
            output += "  z%d_%d := z%d_%d + t%d_%d_%d;\n" % (column+1,line,  column,line, 4,line,column)
        for column in range(line+1, l-1):
            output += "  z%d_%d := z%d_%d + r%d_%d;\n" % (column,line,  column-1,line, line,column)
        output += "\n"

    for i in range(l-1):
        output += "  z[%d] := z%d_%d;\n" % (i, l-2,i)

    output += "\n  (* ----------Phase 4---------- *)\n\n" #######################################

    output += "  z%d_%d := w%d_%d_%d + u%d;\n" % (0,l-1, 4,l-1,0, l-1)

    for line in range(l,l-1+s):
        output += "  ref%d_%d := srnd%d_%d + w%d_%d_%d;\n" % (0,line, line,0, 4,line,0)
        output += "  z%d_%d := ref%d_%d + u%d;\n" % (0,line, 0,line, line)
    output += "\n"

    output += "\n  (* line %d *)\n" % (l-1)
    for column in range(1,l-1):
        output += "  z%d_%d := z%d_%d + w%d_%d_%d;\n" % (column,l-1, column-1,l-1, 4,l-1,column)

    for line in range(1,s):
        output += "\n  (* line %d *)\n" % (line+l-1)
        for column in range(1,l-1):
            output += "  ref%d_%d := srnd%d_%d + w%d_%d_%d;\n" % (column,line+l-1, line+l-1,column, 4,line+l-1,column)
            output += "  z%d_%d := z%d_%d + ref%d_%d;\n" % (column,line+l-1, column-1,line+l-1, column,line+l-1)
        output += "\n"

    output += "\n  (* ----------Refreshing Outputs---------- *)\n\n" #######################################

    output += "  z[%d] := z%d_%d;\n" % (l-1, l-2,l-1)
    for line in range(l,l-1+s):
        output += "  z[%d] := z%d_%d + refZ_%d;\n" % (line, l-2,line, line)

    output += "\nend\n\n"

    output += "order %d noglitch SNI S5_%d_%d_AND\n" % ((l-1),l,s)

    return(output)


if __name__ == '__main__' and '__file__' in globals():
    parser = argparse.ArgumentParser(
        description='description to do later',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-l', '--linear-shares', type=int, default=5,
        help="Number of linear shares"
    )

    parser.add_argument(
        '-s', '--slots', type=int, default=5,
        help="Number of slots"
    )

    args = parser.parse_args()

    print(generateMaskVerifS5(args.linear_shares, args.slots))
