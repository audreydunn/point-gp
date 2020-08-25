from mutation import mutate, mutate_replace, mutate_insert, mutate_shrink
from node_set import PrimitiveSet, TerminalSet
from tree import generate_tree, parse_tree, check_tree_ids
from crossover import one_point_crossover
from copy import deepcopy
import numpy as np
import random

if __name__ == '__main__':
    # We should use strings for dtypes instead of actual types
    # Memory usage:
    # sys.getsizeof("float") = 54
    # sys.getsizeof(float) = 400
    primitive_set = PrimitiveSet()
    # output_type -> (name, input_types, group)
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

    # TODO: Figure out a way for primitives to select specific terminals from the float type (So the user does not have to constantly define new types that do the same thing)
    # Note: Terminals and Ephemeral Constants are the same thing in this framework

    # Generators are functions which will be called when the node is generated
    # The string of the tree will then have the precomputed value
    terminal_set = TerminalSet()
    terminal_set.add_terminal("float", "uniform_0_1", random.random, True)
    terminal_set.add_terminal("x", "pass_x", lambda: "x", True)

    # Generate a random tree
    tree = generate_tree(primitive_set, terminal_set, depth=2)

    # Validate node_ids
    check_tree_ids(tree, "0")

    print("Tree String:\n{}\n".format(str(tree)))
    node_ids = tree.get_tree_ids()
    print("Unique Node IDs:\n{}\n".format(node_ids))
    print("Number of Unique Node IDs:\n{}\n".format(len(node_ids)))
    print("Tree Size (Number of Nodes):\n{}\n".format(tree.size()))
    print("X Input Node IDs:\n{}\n".format(tree.get_input_ids()))

    # Combine function_pointers of primitive_set and terminal_sets
    function_pointers = primitive_set.function_pointers
    function_pointers.update(terminal_set.function_pointers)

    # Generate function pointer for the tree
    func = tree.get_func(function_pointers)

    # Evaluate Tree
    x = np.array([4.6, 7.3, 9.5])
    print("Tree Output:\n{}\n".format(func(x)))

    # Perform mutate replace on the tree
    new_tree = mutate(mutate_replace, primitive_set, terminal_set, deepcopy(tree))

    # Print new tree
    print("Mutate Replace Tree String:\n{}\n".format(str(new_tree)))
    print("Mutate Replace Tree Size (Number of Nodes):\n{}\n".format(new_tree.size()))

    # Validate node_ids
    check_tree_ids(tree, "0")

    # Re-evaluate the tree after the mutation
    func = new_tree.get_func(primitive_set.function_pointers)
    x = np.array([4.6, 7.3, 9.5])
    print("Mutate Replace Tree Output:\n{}\n".format(func(x)))

    # Perform mutate replace on the tree
    new_tree = mutate(mutate_insert, primitive_set, terminal_set, deepcopy(tree), use_input_ids=True)

    # Print new tree
    print("Mutate Insert Tree String:\n{}\n".format(str(new_tree)))
    print("Mutate Insert Tree Size (Number of Nodes):\n{}\n".format(new_tree.size()))

    # Validate node_ids
    check_tree_ids(tree, "0")

    # Re-evaluate the tree after the mutation
    func = new_tree.get_func(primitive_set.function_pointers)
    x = np.array([4.6, 7.3, 9.5])
    print("Mutate Insert Tree Output:\n{}\n".format(func(x)))

    # Perform mutate shrink on the tree
    new_tree = mutate(mutate_shrink, primitive_set, terminal_set, deepcopy(tree))

    # Print new tree
    print("Mutate Shrink Tree String:\n{}\n".format(str(new_tree)))
    print("Mutate Shrink Tree Size (Number of Nodes):\n{}\n".format(new_tree.size()))

    # Validate node_ids
    check_tree_ids(tree, "0")

    # Re-evaluate the tree after the mutation
    func = new_tree.get_func(primitive_set.function_pointers)
    x = np.array([4.6, 7.3, 9.5])
    print("Mutate Shrink Tree Output:\n{}\n".format(func(x)))

    # Generate a new tree for crossover
    second_tree = generate_tree(primitive_set, terminal_set, depth=4)

    # Perform one point crossover
    new_tree, new_tree_2 = one_point_crossover(primitive_set, terminal_set, deepcopy(tree), deepcopy(second_tree))

    # Print new tree
    print("One-Point Crossover Tree String:\n{}\n".format(str(new_tree)))
    print("One-Point Crossover Tree Size (Number of Nodes):\n{}\n".format(new_tree.size()))
    print("Crossover Tree Node IDs:\n{}\n".format(new_tree.get_tree_ids()))
    print("Crossover Tree Number of Unique Node IDs:\n{}\n".format(len(new_tree.get_tree_ids())))
    print("Crossover Tree Input IDs:\n{}\n".format(new_tree.get_input_ids()))

    # Validate node_ids
    check_tree_ids(new_tree, "0")
    check_tree_ids(new_tree_2, "0")

    # Re-evaluate the tree after the mutation
    func = new_tree.get_func(primitive_set.function_pointers)
    x = np.array([4.6, 7.3, 9.5])
    print("One-Point Crossover Tree Output:\n{}\n".format(func(x)))

    raise Exception

    # Test parse_tree on the original tree string
    print("String to parse:\n{}\n".format(tree))
    parsed_tree = parse_tree(str(deepcopy(tree)), primitive_set.struct_by_name(), terminal_set.struct_by_name())
    print("Parsed Tree String:\n{}\n".format(str(parsed_tree)))
    node_ids = parsed_tree.get_tree_ids()
    print("Unique Node IDs:\n{}\n".format(node_ids))
    print("Number of Unique Node IDs:\n{}\n".format(len(node_ids)))
    print("Tree Size (Number of Nodes):\n{}\n".format(parsed_tree.size()))
    print("X Input Node IDs:\n{}\n".format(parsed_tree.get_input_ids()))

    # Generate function pointer for the tree
    func = parsed_tree.get_func(function_pointers)

    # Evaluate Tree
    x = np.array([4.6, 7.3, 9.5])
    print("Tree Output:\n{}\n".format(func(x)))