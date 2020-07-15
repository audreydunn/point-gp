from core import apply_at_node
import random

def mutate(mutation, primitive_set, terminal_set, tree):
    """
    Applies a mutation to the tree

    Args:
        mutation: callable mutation function
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator"}, ...])
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
    apply_at_node(mutation, primitive_set, terminal_set, tree, node_id)


def mutate_replace(primitive_set, tree):
    """
    Randomly selects a node in the tree
    and replaces it with a random node
    of the same type

    Adds additional child nodes as needed

    Args:
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    # Check if we're at a leaf node
    # By checking for any Node objects in tree.args
    if len(tree.args) == 0:
        pass
    else:
        pass

def mutate_insert(primitive_set, tree):
    """
    Randomly selects a node in the tree
    and adds a new node with the current node
    as one of its inputs

    Adds additional child nodes as needed

    Args:
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    pass

def mutate_shrink(primitive_set, tree):
    """
    Randomly selects a node in the tree
    and removes it
    Node is replaced with one of its children

    Args:
        tree: Node containing full tree

    Returns:
        Node containing full tree
    """
    pass