"""
A Tree consists of one root Node linking down to every other node

Tree gets compiled top down
"""
import random

class Node():
    def __init__(self, name, args, id_list, depth=1, parent=None):
        # Set to parent node unless root. Root has no parent
        self.parent = parent

        # 0 .. N children nodes. Leaves have 0 children
        # example args: ["0", child1, "1.0", "2", child2, child3]
        self.args = args

        # string primitive name
        # example: math.sin
        self.name = name

        # Depth node is at in the tree
        # Not sure if this will stay around because 
        # it has to be updated when the tree changes
        self.depth = depth

        # ID used for evolutionary operators
        # Casts to an int to reduce memory usage
        self.id_list = id_list

    def compile(self, pset):
        """
        Recursively converts the tree into a string of function calls
        Then compiles those function calls into a single function call

        This function assumes a single input, x
        Which can be used in multiple places

        Args:
            pset: dictionary where (key, value) is (string, function)

        Returns:
            Single compiled function
        """
        return eval("lambda x: " + self.lisp(), pset, {})

    def lisp(self):
        """
        Recursively converts the tree into a string of function calls
        Based on LISP https://en.wikipedia.org/wiki/Lisp_(programming_language)

        Returns:
            LISP string representation of the 
        """
        return self.name + "(" + "".join([i.lisp() + ", " if isinstance(i, Node) else i + ", " for i in self.args])[:-2] + ")"

    def size(self):
        """
        Recursively calculate the size of the tree

        Returns:
            Number of nodes in the tree
        """
        size = 0
        for i in self.args:
            if isinstance(i, Node):
                size += 1 + i.size()
        return size

    def get_id_list(self):
        """
        Get list of ids

        Returns:
            List containing the ids of every node in the tree
        """
        return self.id_list

def generate(primitive_set, depth, arity, node_id):
    """
    Randomly generate a single tree

    Args:
        primitive_set: dictionary where (key, value) is (primitive name, arity)
        depth:         current depth level
        arity:         number of input variables
        node_id:       string id of the node

    Returns:
        Node containing full tree
    """
    # List of child nodes
    nodes = []
    # Use to differentiate ids
    id_counter = 0

    # Leaf node
    if depth == 1:
        for i in range(arity):
            # Select a random primitive
            primitive = random.choice(list(primitive_set))

            # Set the input of the leaf node to be the original input data
            # primitive_set[primitive] is the arity of the primitive
            args = ["x" for i in range(primitive_set[primitive])]

            # Create the Node and add it to the list of children
            nodes.append(Node(primitive, args, [node_id + str(id_counter)], depth=depth))

            # Increment id counter so each child will have a different id
            id_counter += 1
        
        return nodes

    # All other nodes
    for i in range(arity):
        # Select a random primitive
        primitive = random.choice(list(primitive_set))

        # Generate children nodes
        # primitive_set[primitive] is the arity of the primitive
        p_nodes = generate(primitive_set, depth-1, primitive_set[primitive], node_id + str(id_counter))

        # Create full list of ids by combining the id lists of the children
        id_list = [node_id + str(id_counter)]
        for node in p_nodes:
            id_list += node.get_id_list()
        
        # Create the Node and add it to the list of children
        nodes.append(Node(primitive, p_nodes, id_list, depth=depth))

        # Increment id counter so each child will have a different id
        id_counter += 1

    return nodes


def generate_tree_naive(primitive_set, depth=1):
    """
    Randomly generate a single tree
    Assume every primitive can be used as an output (symbolic regression)
    Assume nothing has non "x" inputs like floats and ints

    Args:
        primitive_set: dictionary where (key, value) is (primitive name, arity)
        depth:         maximum depth of tree

    Returns:
        Node containing full tree
    """
    if depth < 1:
        raise ValueError("Depth must be greater than 0")

    return generate(primitive_set, depth, 1, "")[0]

def apply_at_node(modifier, primitive_set, tree, node_id):
    """
    Recurse through the tree until the node is found
    Then apply an operation to the node
    """
    # We have reached the correct node if the string is empty
    if node_id == "":
        # Apply the modification
        tree = modifier(primitive_set, tree)

        # Return the modified tree node
        return tree

    # Pop the first number off of the start of the node_id

    # This gets casted to an integer so it can be used as an index
    node_index = int(node_id[0])
    # The next node is the correct node if the length of the node_id is 1
    if len(node_id) == 1:
        next_id = ""
    else:
        next_id = node_id[1:]

    # Filter children down to only Nodes
    children = [node for node in enumerate(tree.args) if isinstance(node, Node)]

    # Set the correct child to be the result of the recursion
    tree.args[children[node_index][1]] = apply_at_node(primitive_set, children[node_index][0], next_id)

    return tree

if __name__ == '__main__':
    primitive_set = {"add":2, "subtract":2, "multiply":2, "divide":2}

    tree = generate_tree_naive(primitive_set, depth=4)
    print("Tree String:\n{}".format(tree.lisp()))
    print("Unique Node IDs:\n{}".format(tree.get_id_list()))