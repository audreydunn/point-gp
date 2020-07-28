from tree import apply_at_node, TerminalNode
import random

def mutate(mutation, primitive_set, terminal_set, tree):
    """
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
    node_id = random.choice(tree.get_id_list())

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

def mutate_insert(primitive_set, terminal_set, tree):
    """
    Randomly selects a node in the tree
    and adds a new node with the current node
    as one of its inputs

    Adds additional child nodes as needed

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    pass

def mutate_shrink(primitive_set, terminal_set, tree):
    """
    Randomly selects a node in the tree
    and removes it
    Node is replaced with one of its children

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    pass