
from mutation import mutate, mutate_replace, mutate_insert, mutate_shrink
from node_set import PrimitiveSet, TerminalSet
from tree import generate_tree, parse_tree
from crossover import one_point_crossover
from functools import partial
from copy import deepcopy
import multiprocess
import numpy as np
import random
import sys
import os

# Set random seed
random.seed(101)
np.random.seed(101)

# Pool size
if sys.platform == 'win32':
    num_proc = int(os.environ['NUMBER_OF_PROCESSORS'])
else:
    num_proc = int(os.popen('grep -c cores /proc/cpuinfo').read())
POOL_SIZE = max(2, num_proc - 2)
# print("Using {} processes".format(POOL_SIZE))

# Population size
POP_SIZE = 600

# Number of generations
NGEN = 100

# Mutation probability
MUTPB = 0.25

# Crossover probability
CXPB = 0.96

SEED = "add_x_x(div_x_float(mult_x_x(sub_x_float(sub_x_float(pass_x(x), uniform_5_5(0.3330847400917083)), uniform_5_5(4.762321841272186)), mult_x_x(pass_x(x), pass_x(x))), tan_float(add_float_float(pass_2(2.0), pass_1(1.0)))), div_x_float(sin_x(pass_x(x)), div_float_float(cos_float(pass_2(2.0)), mult_float_float(uniform_5_5(4.709478895399462), uniform_5_5(-3.7382713053737957)))))"

SEED2 = "add_x_x(sub_x_x(sub_x_float(div_x_float(add_x_x(mult_x_x(mult_x_float(pass_x(x), uniform_5_5(4.762321841272186)), sub_x_float(pass_x(x), uniform_5_5(4.762321841272186))), mult_x_float(mult_x_float(cos_x(mult_x_float(pass_x(x), uniform_5_5(4.762321841272186))), pass_3(3.0)), uniform_5_5(4.762321841272186))), pass_2(2.0)), sin_float(pass_1(1.0))), tan_x(mult_x_float(div_x_float(pass_x(x), pass_2(2.0)), pass_3(3.0)))), div_x_x(mult_x_x(add_x_float(pass_x(x), uniform_5_5(1.7955839820267636)), add_x_x(tan_x(tan_x(pass_x(x))), pass_x(x))), div_x_float(exp_x(pass_x(x)), pass_2(2.0))))"

# x^4 + x^3 + x^2 + x
def polynomial(x):
    return np.power(x, 4) + np.power(x, 3) + np.power(x, 2) + x

def polynomial2(x):
    return np.exp(-1.0 * (np.sin(3 * x) + (2 * x)))

def evaluate(function_pointers, individual, x, y):
    # Generate function pointer for the tree
    func = individual[0].get_func(function_pointers)

    # Get output of tree
    output = func(x)

    # Calculate Mean Squared Error
    try:
        error = np.mean(np.square(output - y))
    except:
        print(x, output, y)
        raise

    return error

def mutate_pop(individual, mutpb, primitive_set, terminal_set):
    offspring = []

    # Replace
    if random.random() < mutpb:
        offspring.append((mutate(mutate_replace, primitive_set, terminal_set, deepcopy(individual[0])), None))

    # Insert
    if random.random() < mutpb:
        offspring.append(( mutate(mutate_insert, primitive_set, terminal_set, deepcopy(individual[0]), use_input_ids=True), None))

    # Shrink
    if random.random() < mutpb:
        offspring.append((mutate(mutate_shrink, primitive_set, terminal_set, deepcopy(individual[0])), None))

    return offspring

def crossover_pop(individual_1, individual_2, cxpb):
    offspring = []

    # One-point crossover
    new_tree, new_tree_2 = one_point_crossover(primitive_set, terminal_set, deepcopy(individual_1[0]), deepcopy(individual_2[0]))

    # Add both trees to the offspring
    offspring += [(new_tree, None), (new_tree_2, None)]

    return offspring

if __name__ == '__main__':
    # Create Primitive Set
    primitive_set = PrimitiveSet()
    
    # Add each primitive
    primitive_set.add_primitive(np.add, "x", "add_x_float", ["x", "float"], "operators")
    primitive_set.add_primitive(np.add, "x", "add_x_x", ["x", "x"], "operators")

    primitive_set.add_primitive(np.subtract, "x", "sub_x_float", ["x", "float"], "operators")
    primitive_set.add_primitive(np.subtract, "x", "sub_x_x", ["x", "x"], "operators")

    primitive_set.add_primitive(np.multiply, "x", "mult_x_float", ["x", "float"], "operators")
    primitive_set.add_primitive(np.multiply, "x", "mult_x_x", ["x", "x"], "operators")

    primitive_set.add_primitive(np.divide, "x", "div_x_float", ["x", "float"], "operators")
    primitive_set.add_primitive(np.divide, "x", "div_x_x", ["x", "x"], "operators")

    primitive_set.add_primitive(np.add, "float", "add_float_float", ["float", "float"], "operators")
    primitive_set.add_primitive(np.subtract, "float", "sub_float_float", ["float", "float"], "operators")
    primitive_set.add_primitive(np.multiply, "float", "mult_float_float", ["float", "float"], "operators")
    primitive_set.add_primitive(np.divide, "float", "div_float_float", ["float", "float"], "operators")

    primitive_set.add_primitive(np.sin, "x", "sin_x", ["x"], "operators")
    primitive_set.add_primitive(np.sin, "float", "sin_float", ["float"], "operators")

    primitive_set.add_primitive(np.cos, "x", "cos_x", ["x"], "operators")
    primitive_set.add_primitive(np.cos, "float", "cos_float", ["float"], "operators")

    primitive_set.add_primitive(np.tan, "x", "tan_x", ["x"], "operators")
    primitive_set.add_primitive(np.tan, "float", "tan_float", ["float"], "operators")

    primitive_set.add_primitive(np.log, "x", "log_x", ["x"], "operators")
    primitive_set.add_primitive(np.log, "float", "log_float", ["float"], "operators")

    primitive_set.add_primitive(np.sqrt, "x", "sqrt_x", ["x"], "operators")
    primitive_set.add_primitive(np.sqrt, "float", "sqrt_float", ["float"], "operators")

    primitive_set.add_primitive(np.exp, "x", "exp_x", ["x"], "operators")
    primitive_set.add_primitive(np.exp, "float", "exp_float", ["float"], "operators")

    # Create Terminal Set
    terminal_set = TerminalSet()

    # Add Terminals
    terminal_set.add_terminal("float", "uniform_5_5", partial(random.uniform, -5, 5), True)
    terminal_set.add_terminal("float", "pass_1", lambda: 1.0, True)
    terminal_set.add_terminal("float", "pass_2", lambda: 2.0, True)
    terminal_set.add_terminal("float", "pass_3", lambda: 3.0, True)
    terminal_set.add_terminal("x", "pass_x", lambda: "x", True)

    # Combine function_pointers of primitive_set and terminal_sets
    function_pointers = primitive_set.function_pointers
    function_pointers.update(terminal_set.function_pointers)

    # Create a population
    # Each Individual consists of a tuple: (tree, score)
    population = []
    for i in range(POP_SIZE):
        population.append((generate_tree(primitive_set, terminal_set, depth=4), None))

    # seed = (parse_tree(SEED2, primitive_set.struct_by_name(), terminal_set.struct_by_name()), None)

    # population.append(seed)

    x = []
    y = []
    # Randomly generate 20 points from the polynomial
    for i in range(20):
        x.append(random.uniform(-5, 5))
        y.append(polynomial2(x[-1]))
    x = np.array(x)
    y = np.array(y)

    # Create a pool of processes
    pool = multiprocess.Pool(processes=POOL_SIZE)

    # Evaluate the initial population
    scores = pool.starmap_async(evaluate, [(function_pointers, individual, x, y) for individual in population]).get()
    pool.terminate()

    # Sort by score and take the top 100
    sorted_scores = np.argsort(scores)[:100]

    # Select the top 100 individuals as an elite pool
    population = [(population[i][0], scores[i]) for i in sorted_scores]

    for gen in range(1, NGEN + 1):
        print("Starting Gen:", gen)

        # Create a pool of processes
        pool = multiprocess.Pool(processes=POOL_SIZE)

        # Create list for storing offspring
        offspring = []

        # Mutate elite pool
        for individual in population:
            offspring += mutate_pop(individual, MUTPB, primitive_set, terminal_set)

        # Crossover elite pool
        for individual_1 in population:
            if random.random() < CXPB:
                offspring += crossover_pop(individual_1, random.choice(population), CXPB)

        # # Mutate elite pool
        # new_individuals = pool.starmap_async(mutate_pop, [(individual, MUTPB, primitive_set, terminal_set) for individual in population]).get()
        # for i in new_individuals:
        #     offspring += i

        # # Crossover elite pool
        # new_individuals = pool.starmap_async(crossover_pop, [(individual, CXPB, primitive_set, terminal_set) for individual in population]).get()
        # for i in new_individuals:
        #     offspring += i

        print("Number of offspring:", len(offspring))

        # Evaluate the offspring
        scores = pool.starmap_async(evaluate, [(function_pointers, individual, x, y) for individual in offspring]).get()
        pool.terminate()

        # Combine offspring scores with elite pool scores
        scores = scores + [i[1] for i in population]

        # Combine elite pool and offspring
        population = offspring + population

        # Sort by score and take the top 100
        sorted_scores = np.argsort(scores)[:100]

        # Select the top 100 individuals as an elite pool
        population = [(population[i][0], scores[i]) for i in sorted_scores]

        print("Best Score:", population[0][1])

    print("Best individual:", str(population[0][0]), population[0][1])
