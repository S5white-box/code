S5: Combining white-box countermeasures to withstand automated attacks
======================================================================

This repository contains implementations and logs for the anonymous submission at Eurocrypt 2025.

**Requirements:**

The different implementations require python3 together with `wboxkit` (https://github.com/hellman/wboxkit) and the `MaskVerif` tool (https://gitlab.com/benjgregoire/maskverif/).



Generating S5 or ISWoDS circuits
------------------------------

Generating circuits uses the `wboxkit` tool, and can be done by calling `createS5.py` (which uses the file `S5.py` to define its gadgets in the `wboxkit` tool) or `createISWoDS.py` with python3. These two files use the same optional parameters:


**Parameters:**

- **-l:** *The number of linear shares.* The number of shares of S5 with one of them being slotted, and the number of shares of ISW for ISWoDS. Default value: 3.

- **-s:** *The number of slots.* The number of slots to spread one of the shares of S5, and the number of slots of Dummy Shuffling for ISWoDS. Default value: 3.

- **-r:** *The number of the base AES rounds.* Default value: 10 (two rounds is enough to perform white-box attacks and results in lighter traces stored).


**Example:** ``python3 createS5.py -l 4 -s 3 -r 10`` will applies S5 with 4 linear shares and 3 slots to a 10-round AES, and puts the resulting circuit "aes10_S5_4_3.bin" into the folder "circuits", which can be converted into traces using the wboxkit tool, for instance 256 traces with the command: ``wboxkit.trace -T 256 circuits/aes10_S5_4_3.bin traces/``.



Verifying S5 Strong Non-Interference
------------------------------------

To verify the Strong Non-Interference of S5's and gadget, we use the `MaskVerif` tool, which uses a unique syntax.

**Caution:** MaskVerif should be in PATH. You can modify the `VerifyS5.sh` shell script to link it.

The python script `SNIS5verification.py` takes for input the number of linear shares and slots of S5, and prints its corresponding and gadget in the `MaskVerif` format. For these implementations, we fix the main slot, which can only lower the SNI security while still being able to prove it using the tool. This output can be converted into a python file with the `VerifyS5.py` script to ensure its ability to compute correct output. To perform all of these operations, one can run the `VerifyS5.sh` bash script, which has for parameters:

**Parameters:**

- **#1:** *The number of linear shares of S5.*

- **#2:** *The number of slots of S5.*


**Example:** ``bash -x VerifyS5.sh 4 5`` will verify that S5 with 4 linear shares and 5 slots is SNI, and that the implementation verified by MaskVerif is correctly computing the AND of the shares for 100 random inputs.

**Logs:** All of our logs for the verifications for every 1<l<8 and 1<s<8 can be found in the repository `logs/SNI/`.


Comparing implementation sizes of S5 with ISWoDS, and C_DSoISW
--------------------------------------------------------------

The python script `ComparisonS5.py` allows display on the screen the different implementation sizes of S5, ISWoDS, and DSoISW, whith `l` linear shares and `s` slots, applied to a `r` round AES.

**Parameters:**

- **-l:** *The number of linear shares.* The number of shares of S5 with one of them being slotted, and the number of shares of ISW for ISWoDS. Default value: 3.

- **-s:** *The number of slots.* The number of slots to spread one of the shares of S5, and the number of slots of Dummy Shuffling for ISWoDS. Default value: 3.

- **-r:** *The number of the base AES rounds.* Default value: 10 (two rounds is enough to perform white-box attacks and results in lighter traces stored).

**Example:** `python3 ComparisonS5.py -l 2 -s 4 -r 2` will display the different stats (number of xor, and, not gates, and how much more it is compared to the base AES) of the three implementations for 2 linear shares, 4 slots onto a 2-round AES.

**Logs:** All of our logs for implementation sizes for  every 1<l<8 and 1<s<8 can be found in the repository `logs/Comparison/`.
