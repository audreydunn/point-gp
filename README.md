# point-gp
Genetic Programming Library built on Node-Linked Trees

Required Python Packages:
- numpy

Usage: python main.py

Features:
- Randomly generate trees of any depth
- Use your own functions and distributions in the trees using PrimitiveSet and TerminalSet
- Create and Save trees using LISP string representations. Example: mult_float_float(uniform_0_1(0.18075552810664686), uniform_0_1(0.07689517676260194))
- Mutate trees using 3 different mutation operators: Replace, Insert, and Shrink
- Crossover (Mate) trees using One-Point-Crossover