from tree import apply_at_node
import random

def one_point_crossover(tree_1, tree_2):
    """
    Picks a point in each tree and swaps
    the corresponding subtrees

    Args:
        tree_1: Node containing full tree
        tree_2: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Randomly choose a node in the first tree
    # TODO: Change this to be a common point between both trees
    # Or randomly choose a different point in each tree?
    node_id = random.choice(tree_1.get_id_list())

    # Take off root id
    node_id = node_id[1:]

    # Recurse through the tree until the node is found
    # TODO: Find a good design for 2 trees
    # *args design should work
    # Example: apply_at_node(tree_1, node_id, func, *func_args)