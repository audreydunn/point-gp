"""
This file contains crossover functions
"""
from functools import partial
from copy import deepcopy
import random

def swap_subtree(subtree, tree, node_id):
    """
    Args:
        subtree: New tree
        tree: Original tree
    
    Returns:
        Tree object with node swapped with subtree
    """
    # Regenerate node ids of the new subtree given the node id of the original tree
    subtree.regenerate_node_ids(node_id, "")

    # Recursively remove the original subtree
    tree.remove(node_id)

    # Add the new subtree to the original tree
    tree.nodes.update(subtree.nodes)

    # Delete the subtree object for garbage collection
    del subtree

    # Return updated tree
    return tree

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
    output_type = tree_1.nodes[node_id].output_type

    # Find nodes with the same output_type in the second tree
    valid_node_ids = []
    for n in tree_2.nodes:
        if tree_2.nodes[n].output_type == output_type:
            valid_node_ids.append(n)

    if len(valid_node_ids) == 0:
        # Rerun function without invalid output_type
        return find_valid_nodes([i for i in node_ids if tree_1.nodes[i].output_type != output_type], tree_1, tree_2)

    # Get subtree object from tree_1
    subtree_1 = tree_1.get_subtree(node_id)

    # Randomly choose a node in the second
    valid_node_id = random.choice(valid_node_ids)

    # Get subtree object from tree_2
    subtree_2 = tree_2.get_subtree(valid_node_id)

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

    # Apply crossover to tree_1
    new_tree_1 = swap_subtree(subtree_2, deepcopy(tree_1), node_id_2)

    # Apply crossover to tree_2
    new_tree_2 = swap_subtree(subtree_1, deepcopy(tree_2), node_id_1)

    return new_tree_1, new_tree_2