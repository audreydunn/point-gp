"""
This file contains mutation functions
"""
from tree import apply_at_node, TerminalNode, generate
import random

def mutate(mutation, primitive_set, terminal_set, tree, use_input_ids=False):
    """
    TODO: Find a better way to implement use_input_ids
    Applies a mutation to the tree

    Args:
        mutation: callable mutation function
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Randomly choose a node
    node_id = random.choice(tree.get_input_ids()) if use_input_ids else random.choice(tree.get_tree_ids())

    # Take off root id
    node_id = node_id[1:]

    # Recurse through the tree until the node is found
    # Then apply the mutation
    return apply_at_node(mutation, primitive_set, terminal_set, tree, node_id)

def mutate_replace(primitive_set, terminal_set, tree):
    """
    Randomly selects a node in the tree
    and replaces it with a random node
    of the same type

    With the same input and output types

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Check if we're at a Terminal node
    # Terminal nodes are also leaf nodes
    # Terminal nodes do not have arguments
    if len(tree.args) == 0:
        # Mutate Terminal

        # Sanity check
        if not isinstance(tree, TerminalNode):
            raise Exception("Node reached in mutate_replace has empty args and is not a TerminalNode.")

        # There are two ways to mutate the terminal:
        # 1. Regenerate the terminal value
        # 2. Change the terminal into another terminal with the same output type (if one exists)
        if tree.static:
            # Regenerate terminal value
            tree.regenerate()
        else:
            # Search for a different terminal with the same output type
            # Note: It is possible to get the same terminal type again
            # But the terminal value will still be mutated
            new_terminal = random.choice(terminal_set.node_set[tree.output_type])

            # Mutate the terminal generator
            tree.mutate_generator(new_terminal["generator"])

    else:
        # Mutate Primitive

        # Search for a primitive with the same output type
        # And the same input types
        # TODO: Try to Optimize this 
        matching_primitives = []
        for primitive in primitive_set.node_set[tree.output_type]:
            if primitive["input_types"] == tree.input_types:
                matching_primitives.append(primitive["name"])

        # matching_primitives is never empty in the case
        # Because the current primitive will always be in the list
        # TODO: Only select from new primitives
        if len(matching_primitives) > 0:
            # Mutate the primitive function by changing the name
            tree.set_name(random.choice(matching_primitives))

    # Return modified tree
    return tree

def cleanup_mutated_node_ids(tree):
    """
    Removes incorrect characters from node_ids of a tree
    Only works on trees with depth 1

    Args:
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Remove the "0" added to the end of the parent id
    tree.node_id = tree.node_id[:-1]

    # Remove the "0" added to the child ids
    for i in range(len(tree.args)):
        # Remove second to last character
        tree.args[i].node_id = tree.args[i].node_id[:-2] + tree.args[i].node_id[-1]
        # Update child id lists
        tree.args[i].update_tree_ids()
        # Update input_ids if output type is "x"
        if tree.args[i].output_type == "x":
            tree.args[i].input_ids = [tree.args[i].node_id]

    # Update parent id lists
    tree.update_tree_ids()
    tree.update_input_ids()

    return tree

def mutate_insert(primitive_set, terminal_set, tree):
    """
    Randomly selects a Terminal with output type "x"
    and generates new subtree in place of it with depth 1

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    return cleanup_mutated_node_ids(generate(primitive_set, terminal_set, 1, ["x"], tree.node_id)[0])

def mutate_shrink(primitive_set, terminal_set, tree):
    """
    Randomly selects a node in the tree
    and replaces the entire subtree
    with a terminal of the same output type

    TODO: Make a variation of this that replaces the node
    with its real output value instead

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Choose a random terminal with the same output type as tree
    terminal = random.choice(terminal_set.node_set[tree.output_type])

    # Pass node_id of this Terminal if input_type is x
    input_ids = [tree.node_id] if tree.output_type == "x" else []

    # Create a new TerminalNode
    return TerminalNode(terminal["name"], 
                        [], tree.node_id, {tree.node_id:tree.output_type}, input_ids,
                        tree.output_type, terminal["generator"], terminal["static"])