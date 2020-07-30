"""
A Tree consists of one root Node linking down to every other node

Tree gets compiled top down

TODO: Make node_id list recursive
"""
import random

class Node():
    def __init__(self, name, args, node_id, id_list, x_list, output_type, input_types):
        
        # 0 .. N children nodes. Leaves have 0 children
        # example args: ["0", child1, "1.0", "2", child2, child3]
        self.args = args

        # string primitive name
        # example: math.sin
        self.name = name

        # Data type of the node
        # This is the output type
        self.output_type = output_type

        # Input types of the node
        # Used for evolutionary operators
        self.input_types = input_types

        # Node ID of this node
        # Used to update id_list
        self.node_id = node_id

        # ID used for evolutionary operators
        self.id_list = id_list

        # List of IDs for terminal nodes with "x" output_type
        # Used for evolutionary operators
        self.x_list = x_list

    def get_func(self, func_pointers):
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
        return eval("lambda x: " + self.__str__(), func_pointers, {})

    def get_id_list(self):
        """
        Get list of ids

        Returns:
            List containing the ids of every node in the tree
        """
        return self.id_list

    def get_x_list(self):
        """
        Get list of ids
        Where each id is a terminal node with output_type "x"

        Returns:
            List containing the ids of every terminal node with output_type "x" in the tree
        """
        return self.x_list

    def update_id_list(self):
        """
        Updates id_list by adding together the id_list of every child
        """
        self.id_list = [self.node_id]
        for i in self.args:
            self.id_list += i.get_id_list()

    def update_x_list(self):
        """
        Updates x_list by adding together the x_list of every child
        """
        self.x_list = []
        for i in self.args:
            self.x_list += i.get_x_list()

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

    def set_name(self, name):
        """
        Replace primitive name with a new one
        This mutates what the primitive function is

        Args:
            name: string name of the primitive
        """
        self.name = name

    def __str__(self):
        """
        Recursively converts the tree into a string of function calls
        Based on LISP https://en.wikipedia.org/wiki/Lisp_(programming_language)

        Returns:
            LISP string representation of the tree
        """
        return self.name + "(" + "".join([str(i) + ", " for i in self.args])[:-2] + ")"

class TerminalNode(Node):
    def __init__(self, name, args, node_id, id_list, x_list, output_type, generator, static, input_types=None):
        super().__init__(name, args, node_id, id_list, x_list, output_type, input_types)

        # String of the terminal value
        # This should be a python primitive (float, int, str, list, etc ...)
        # We store this as a string in memory to reduce memory usage
        # The value can always be cast into its original type
        self.value = str(generator())

        # Save function reference for regenerating terminal value
        self.generator = generator

        # Boolean for whether terminal generator can be changed
        self.static = static

    def regenerate(self):
        """
        Replace terminal value with a new one from the generator

        This may generate the same value as the current one
        """
        self.value = str(self.generator())

    def mutate_generator(self, generator):
        """
        Replace terminal generator with a new generator
        And generate a new value using the new generator

        Args:
            generator: function reference of a generator
        """
        # Save function reference for regenerating terminal value
        self.generator = generator

        # String of the terminal value
        self.value = str(generator())

    def __str__(self):
        """
        Returns:
            string representation of terminal value
        """
        return self.value

def generate(primitive_set, terminal_set, depth, output_types, node_id):
    """
    Randomly generate a single tree

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
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
            primitive = random.choice(primitive_set.node_set[output_type])

            # Create current node_id
            curr_node_id = node_id + str(id_counter)

            # Keeps track of the terminal node ids
            # Starts with the node id of the parent
            node_ids = [curr_node_id]

            # Keep track of "x" input Terminals
            x_list = []

            # Set the leaf nodes to be Terminal Nodes
            term_args = []
            id_counter_term = 0
            for input_type in primitive["input_types"]:
                # Choose a random terminal with the correct output type
                terminal = random.choice(terminal_set.node_set[input_type])

                # Calculate node id of this Terminal
                term_node_id = curr_node_id + str(id_counter_term)

                # Pass node_id of this Terminal if input_type is x
                x_list_temp = [term_node_id] if input_type == "x" else []

                # Create a new TerminalNode
                term_args.append(TerminalNode(terminal["name"], 
                                         [], term_node_id, [term_node_id], x_list_temp,
                                         input_type, terminal["generator"], terminal["static"]))
                # Add terminal node id to the node id list
                node_ids.append(term_node_id)
                # Add terminal x_list to the parent's x_list
                x_list += x_list_temp
                # Increment terminal id counter so each terminal will have a different id
                id_counter_term += 1

            # Create the Node and add it to the list of children
            nodes.append(Node(primitive["name"], term_args, curr_node_id, 
                              node_ids, x_list, output_type, primitive["input_types"]))

            # Increment id counter so each child will have a different id
            id_counter += 1
        
        return nodes

    # All other nodes
    for output_type in output_types:
        # Select a random primitive with the correct output type
        primitive = random.choice(primitive_set.node_set[output_type])

        # Create current node_id
        curr_node_id = node_id + str(id_counter)

        # Generate children nodes
        # One for each input type
        p_nodes = generate(primitive_set, terminal_set, depth-1, primitive["input_types"], curr_node_id)

        # Create full list of ids by combining the id lists of the children
        id_list = [curr_node_id]
        for node in p_nodes:
            id_list += node.get_id_list()
        
        # Combine x_list of children
        x_list = []
        for node in p_nodes:
            x_list += node.get_x_list()
        
        # Create the Node and add it to the list of children
        nodes.append(Node(primitive["name"], p_nodes, curr_node_id, id_list, x_list, output_type, primitive["input_types"]))

        # Increment id counter so each child will have a different id
        id_counter += 1

    return nodes

def generate_tree(primitive_set, terminal_set, depth=1, ):
    """
    Randomly generate a single tree
    Assume every primitive can be used as an output (symbolic regression)
    Assume nothing has non "x" inputs like floats and ints

    Args:
        primitive_set: dictionary where (key, value) is (output_type, [{"name", "input_types", "group"}, ...])
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
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
        terminal_set:  dictionary where (key, value) is (output_type, [{"name", "generator", "static"}, ...])
        tree: Node containing full tree
        node_id: string id directing which nodes to traverse

    Returns:
        Node containing full tree
    """
    # We have reached the correct node if the string is empty
    if node_id == "":
        # Apply the modification
        tree = modifier(primitive_set, terminal_set, tree)

        # Update the id_list and x_list of the tree
        tree.update_id_list()
        tree.update_x_list()

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

    # Set the correct child to be the result of the recursion
    tree.args[node_index] = apply_at_node(modifier, primitive_set, terminal_set, tree.args[node_index], next_id)

    # Update the id_list and x_list of the tree
    tree.update_id_list()
    tree.update_x_list()

    return tree