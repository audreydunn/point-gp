"""
This file contains mutation functions
"""
from tree import TerminalNode, generate
import random

def mutate(mutation, primitive_set, terminal_set, tree, use_input_ids=False):
    """
    TODO: Find a better way to implement use_input_ids
    Applies a mutation to the tree

    Args:
        mutation: callable mutation function
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: tree object containing nodes
    """
    # Randomly choose a node
    node_id = random.choice([key for key in tree.nodes if len(tree.nodes[key].children) == 0 and tree.nodes[key].output_type == "x"]) if use_input_ids else random.choice(list(tree.nodes.keys()))

    # Apply the mutation at the node
    tree.nodes[node_id] = mutation(primitive_set, terminal_set, tree, node_id)

    return tree

def mutate_replace(primitive_set, terminal_set, tree, node_id):
    """
    Randomly selects a node in the tree
    and replaces it with a random node
    of the same type

    With the same input and output types

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: tree object containing nodes
        node_id: id of the randomly selected node

    Returns:
        Updated Node
    """
    node = tree.nodes[node_id]

    # Check if we're at a Terminal node
    # Terminal nodes are also leaf nodes
    # Terminal nodes do not have arguments
    if len(node.children) == 0:
        # Mutate Terminal

        # Sanity check
        if not isinstance(node, TerminalNode):
            raise Exception("Node reached in mutate_replace has empty args and is not a TerminalNode.")

        # There are two ways to mutate the terminal:
        # 1. Regenerate the terminal value
        # 2. Change the terminal into another terminal with the same output type (if one exists)
        if node.static:
            # Regenerate terminal value
            node.regenerate()
        else:
            # Search for a different terminal with the same output type
            # Note: It is possible to get the same terminal type again
            # But the terminal value will still be mutated
            new_terminal = random.choice(terminal_set.node_set[node.output_type])

            # Mutate the terminal generator
            node.mutate_generator(new_terminal["generator"])

    else:
        # Mutate Primitive

        # Search for a primitive with the same output type
        # And the same input types
        # TODO: Try to Optimize this 
        matching_primitives = []
        for primitive in primitive_set.node_set[node.output_type]:
            if primitive["input_types"] == node.input_types:
                matching_primitives.append(primitive["name"])

        # matching_primitives is never empty in the case
        # Because the current primitive will always be in the list
        # TODO: Only select from new primitives
        if len(matching_primitives) > 0:
            # Mutate the primitive function by changing the name
            node.set_name(random.choice(matching_primitives))

    # Return modified tree
    return node

def cleanup_mutated_node_ids(tree, node_id, new_tree):
    """
    Inserts the new_tree into the original tree
    Only works on trees with depth 1

    Args:
        tree: Original tree object
        node_id: id of the randomly selected node
        new_tree: Generated tree to insert

    Returns:
        Updated original tree
    """
    # List for child node ids
    children = []

    # Remove root node from original tree
    del tree.nodes[node_id]

    # Replace the root of the new tree with the correct node_id
    # Remove the "0" added to the end of the parent id
    new_tree[node_id] = new_tree.pop(node_id + "0", None)

    # Remove the "0" added to the child ids
    for n_id in new_tree[node_id].children:
        # Remove second to last character and update nodes
        new_id = n_id[:-2] + n_id[-1]
        new_tree[new_id] = new_tree.pop(n_id, None)

        # Add node ids to list of children
        children.append(new_id)

    # Update original tree nodes
    tree.nodes.update(new_tree)

    # Update children
    tree.nodes[node_id].children = children

    return tree.nodes[node_id]

def mutate_insert(primitive_set, terminal_set, tree, node_id):
    """
    TODO: Make this better and not tied to only type "x"
    Randomly selects a Terminal with output type "x"
    and generates new subtree in place of it with depth 1

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: tree object containing nodes
        node_id: id of the randomly selected node

    Returns:
        Updated Node
    """
    nodes, child_ids = generate(primitive_set, terminal_set, 1, ["x"], node_id)

    return cleanup_mutated_node_ids(tree, node_id, nodes)

def mutate_shrink(primitive_set, terminal_set, tree, node_id):
    """
    Randomly selects a node in the tree
    and replaces the entire subtree
    with a terminal of the same output type

    TODO: Make a variation of this that replaces the node
    with its real output value instead

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: tree object containing nodes
        node_id: id of the randomly selected node

    Returns:
        TerminalNode with the same output as the selected node
    """
    # Store the output type
    output_type = tree.nodes[node_id].output_type

    # Choose a random terminal with the same output type as the selected node
    terminal = random.choice(terminal_set.node_set[output_type])

    # Recursively remove nodes from the tree
    tree.remove(node_id)

    # Create a new TerminalNode
    return TerminalNode(terminal["name"], [], output_type, 
                        terminal["generator"], terminal["static"])