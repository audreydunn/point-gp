"""
This file contains crossover functions
"""
from tree import apply_at_node, find_subtree
from functools import partial
import random

def swap_subtree(subtree, primitive_set, terminal_set, tree):
    """
    Args:
        subtree: New tree
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Original tree
    
    Returns:
        Subtree with correct node ids
    """
    # Note: Regenerating the node ids is inefficient here, but improves performance of finding nodes
    # Regenerate node ids of the new subtree given the node id of the original tree
    subtree.regenerate_node_ids(tree.node_id, "")

    # Return updated subtree
    return subtree

def find_valid_nodes(node_ids, tree_1, tree_2):
    """
    Recursive function for finding a subtree in the second tree 
    with the same output type of a random subtree in the first tree

    Args:
        node_ids: List of node ids to search
        tree_1: Node containing full tree
        tree_2: Node containing full tree

    Returns:
        Random subtree of the first tree AND a valid node id of the second tree
        The output_type of the subtree will match the output_type 
        of the valid node of the second tree
    """
    # Randomly choose a node in the first tree
    node_id = random.choice(node_ids)

    # Get output_type of the random node in first tree
    output_type = tree_1.get_id_outputs()[node_id]

    # Find a random node in the second tree with the same output type
    valid_node_ids = []
    for n in tree_2.get_id_outputs():
        if tree_2.get_id_outputs()[n] == output_type:
            valid_node_ids.append(n)

    if len(valid_node_ids) == 0:
        # Rerun function without invalid output_type
        return find_valid_nodes([i for i in node_ids if tree_1.get_id_outputs()[i] != output_type], tree_1, tree_2)

    # Take off root id
    node_id = node_id[1:]

    # Get subtree object from tree_1
    subtree_1 = find_subtree(tree_1, node_id)

    # Randomly choose a node in the second
    valid_node_id = random.choice(valid_node_ids)

    # Take off root id
    valid_node_id = valid_node_id[1:]

    # Get subtree object from tree_2
    subtree_2 = find_subtree(tree_2, valid_node_id)

    return subtree_1, valid_node_id, subtree_2, node_id

def one_point_crossover(primitive_set, terminal_set, tree_1, tree_2):
    """
    Picks a random node with the same output type in each tree 
    and swaps the corresponding subtrees

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree_1: Node containing full tree
        tree_2: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Find a random subtree of the first tree AND a valid node id of the second tree
    subtree_1, node_id_1, subtree_2, node_id_2 = find_valid_nodes(tree_1.get_tree_ids(), tree_1, tree_2)

    # Recurse through the tree until the node is found
    # Then apply the crossover
    return apply_at_node(partial(swap_subtree, subtree_1), primitive_set, terminal_set, tree_2, node_id_1), apply_at_node(partial(swap_subtree, subtree_2), primitive_set, terminal_set, tree_1, node_id_2)