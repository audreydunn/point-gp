"""
A Tree consists of one root Node linking down to every other node

Tree gets compiled top down
"""
import random

class Node():
    def __init__(self, name, args, id_list, output_type):
        
        # 0 .. N children nodes. Leaves have 0 children
        # example args: ["0", child1, "1.0", "2", child2, child3]
        self.args = args

        # string primitive name
        # example: math.sin
        self.name = name

        # Data type of the node
        # This is the output type
        self.output_type = output_type

        # ID used for evolutionary operators
        # Casts to an int to reduce memory usage
        self.id_list = id_list

    def get_func(self, pset):
        """
        Recursively converts the tree into a string of function calls
        Then wraps those function calls into a single function call

        This function assumes a single input, x
        Which can be used in multiple places

        Args:
            pset: dictionary where (key, value) is (string, function)

        Returns:
            Callable function of the tree
        """
        return eval("lambda x: " + self.__str__(), pset, {})

    def get_id_list(self):
        """
        Get list of ids

        Returns:
            List containing the ids of every node in the tree
        """
        return self.id_list

    def size(self):
        """
        Recursively calculate the size of the tree

        Returns:
            Number of nodes in the tree
        """
        # Size starts at 1 to count this node
        size = 1
        for i in self.args:
            if isinstance(i, Node):
                size += i.size()
        return size

    def __str__(self):
        """
        Recursively converts the tree into a string of function calls
        Based on LISP https://en.wikipedia.org/wiki/Lisp_(programming_language)

        Returns:
            LISP string representation of the tree
        """
        return self.name + "(" + "".join([str(i) + ", " if isinstance(i, Node) else i + ", " for i in self.args])[:-2] + ")"

class TerminalNode(Node):
    def __init__(self, name, args, id_list, output_type, generator):
        super().__init__(name, args, id_list, output_type)

        # String of the terminal value
        # This should be a python primitive (float, int, str, list, etc ...)
        # We store this as a string in memory to reduce memory usage
        # The value can always be cast into its original type
        self.value = str(generator())

    def __str__(self):
        """
        Returns:
            string representation of terminal value
        """
        return self.value

# TODO: Rewrite this to be strongly typed
def generate_naive(primitive_set, depth, arity, node_id):
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
            nodes.append(Node(primitive, args, [node_id + str(id_counter)], None))

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
        nodes.append(Node(primitive, p_nodes, id_list, None))

        # Increment id counter so each child will have a different id
        id_counter += 1

    return nodes

def generate(primitive_set, terminal_set, depth, output_types, node_id):
    """
    Randomly generate a single tree

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator"}, ...])
        depth:         current depth level
        output_types:  list of primitive types to generate
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
        for output_type in output_types:
            # Select a random primitive with the correct output type
            primitive = random.choice(primitive_set[output_type])

            # Keeps track of the terminal node ids
            # Starts with the node id of the parent
            node_ids = [node_id + str(id_counter)]

            # Set the leaf nodes to be Terminal Nodes
            term_args = []
            id_counter_term = 0
            for input_type in primitive["input_types"]:
                # Choose a random terminal with the correct output type
                terminal = random.choice(terminal_set[input_type])
                # Create a new TerminalNode
                term_args.append(TerminalNode(terminal["name"], 
                                         [], [node_id + str(id_counter) + str(id_counter_term)], 
                                         input_type, terminal["generator"]))
                # Add terminal node id to the node id list
                node_ids.append(node_id + str(id_counter) + str(id_counter_term))
                # Increment terminal id counter so each terminal will have a different id
                id_counter_term += 1

            # Create the Node and add it to the list of children
            nodes.append(Node(primitive["name"], term_args, node_ids, output_type))

            # Increment id counter so each child will have a different id
            id_counter += 1
        
        return nodes

    # All other nodes
    for output_type in output_types:
        # Select a random primitive with the correct output type
        primitive = random.choice(primitive_set[output_type])

        # Generate children nodes
        # One for each input type
        p_nodes = generate(primitive_set, terminal_set, depth-1, primitive["input_types"], node_id + str(id_counter))

        # Create full list of ids by combining the id lists of the children
        id_list = [node_id + str(id_counter)]
        for node in p_nodes:
            id_list += node.get_id_list()
        
        # Create the Node and add it to the list of children
        nodes.append(Node(primitive["name"], p_nodes, id_list, output_type))

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

    # TODO: First node should have the "x" output type

    return generate_naive(primitive_set, depth, 1, "")[0]

def generate_tree(primitive_set, terminal_set, depth=1):
    """
    Randomly generate a single tree
    Assume every primitive can be used as an output (symbolic regression)
    Assume nothing has non "x" inputs like floats and ints

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator"}, ...])
        depth:         maximum depth of tree

    Returns:
        Node containing full tree
    """
    if depth < 1:
        raise ValueError("Depth must be greater than 0")

    return generate(primitive_set, terminal_set, depth, ["x"], "")[0]

def apply_at_node(modifier, primitive_set, terminal_set, tree, node_id):
    """
    Recurse through the tree until the node is found
    Then apply an operation to the node

    Args:
        modifier: callable function that modifies a Node
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator"}, ...])
        tree: Node containing full tree
        node_id: string id directing which nodes to traverse

    Returns:
        Node containing full tree
    """
    # We have reached the correct node if the string is empty
    if node_id == "":
        # Apply the modification
        tree = modifier(primitive_set, terminal_set, tree)

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
    # OLD Primitive Set
    # primitive_set = {"add":2, "subtract":2, "multiply":2, "divide":2}

    # We should use strings for dtypes instead of actual types
    # Memory usage:
    # sys.getsizeof("float") = 54
    # sys.getsizeof(float) = 400
    # TODO: Automate the creation of the primitive set
    # output_type -> (name, input_types, group)
    primitive_set = {"x": [{"name": "add_x_float", "input_types": ["x", "float"], "group": "operators"},  
                           {"name": "add_x_x", "input_types": ["x", "x"], "group": "operators"},

                           {"name": "sub_x_float", "input_types": ["x", "float"], "group": "operators"}, 
                           {"name": "sub_x_x", "input_types": ["x", "x"], "group": "operators"},

                           {"name": "mult_x_float", "input_types": ["x", "float"], "group": "operators"}, 
                           {"name": "mult_x_x", "input_types": ["x", "x"], "group": "operators"},

                           {"name": "div_x_float", "input_types": ["x", "float"], "group": "operators"}, 
                           {"name": "div_x_x", "input_types": ["x", "x"], "group": "operators"}],

                     "float": [{"name": "add_float_float", "input_types": ["float", "float"], "group": "operators"},
                               {"name": "sub_float_float", "input_types": ["float", "float"], "group": "operators"},
                               {"name": "mult_float_float", "input_types": ["float", "float"], "group": "operators"},
                               {"name": "div_float_float", "input_types": ["float", "float"], "group": "operators"}]
                    }

    # TODO: Figure out a way for primitives to select specific terminals from the float type (So the user does not have to constantly define new types that do the same thing)
    # Note: Terminals and Ephemeral Constants are the same thing in this framework

    # Generators are functions which will be called when the node is generated
    # The string of the tree will then have the precomputed value
    terminal_set = {"float": [{"name": "uniform[0,1]", "generator": random.random}],
                    "x": [{"name": "default", "generator": lambda: "x"}]
                   }

    tree = generate_tree(primitive_set, terminal_set, depth=4)
    print("Tree String:\n{}\n".format(str(tree)))
    node_ids = tree.get_id_list()
    print("Unique Node IDs:\n{}\n".format(node_ids))
    print("Number of Unique Node IDs:\n{}\n".format(len(node_ids)))
    print("Tree Size (Number of Nodes):\n{}\n".format(tree.size()))
    # TODO: Create functions for the primitives, so tree.compile() can be tested