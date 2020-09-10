"""
A Tree consists of one root Node linking down to every other node

Tree gets compiled top down

TODO: Make node_id list recursive
"""
import random
import ast

class Node():
    def __init__(self, name, args, node_id, tree_ids, input_ids, output_type, input_types):
        
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
        # Used to update tree_ids
        self.node_id = node_id

        # List of all the ids of the nodes in the tree
        self.tree_ids = [i for i in tree_ids.keys()]

        # Dictionary of all the ids of the nodes in the tree
        # Mapped to output_type. ex. 01 -> "float"
        self.id_outputs = tree_ids

        # List of IDs for terminal nodes with "x" output_type
        # Used for evolutionary operators
        self.input_ids = input_ids

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

    def get_tree_ids(self):
        """
        Get list of ids

        Returns:
            List containing the ids of every node in the tree
        """
        return self.tree_ids

    def get_id_outputs(self):
        """
        Get Dictionary of all the ids of the nodes in the tree
        Mapped to output_type. ex. 01 -> "float"

        Returns:
            Dictionary containing mapping from id -> output_type
        """
        return self.id_outputs

    def get_input_ids(self):
        """
        Get list of ids
        Where each id is a terminal node with output_type "x"

        Returns:
            List containing the ids of every terminal node with output_type "x" in the tree
        """
        return self.input_ids

    def update_tree_ids(self):
        """
        Updates tree_ids by adding together the tree_ids of every child
        """
        self.tree_ids = [self.node_id]
        self.id_outputs = {self.node_id:self.output_type}
        for i in self.args:
            self.tree_ids += i.get_tree_ids()
            self.id_outputs.update(i.get_id_outputs())

    def update_input_ids(self):
        """
        Updates input_ids by adding together the input_ids of every child
        """
        # Only update if the node is not a TerminalNode
        if len(self.args) != 0:
            self.input_ids = []
            for i in self.args:
                self.input_ids += i.get_input_ids()

    def regenerate_node_ids(self, node_id, position):
        """
        Recursively updates all of the node ids of the tree
        Starting from the given node_id

        Args:
            node_id: new starting node_id of the tree
            position: string corresponding to the position of the node under the root
        """
        self.node_id = node_id + position
        self.tree_ids = [self.node_id]
        self.id_outputs = {self.node_id:self.output_type}

        # If terminal with output_type x
        if len(self.args) == 0 and self.output_type == "x":
            self.input_ids = [self.node_id]
        else:
            self.input_ids = []

            for i, node in enumerate(self.args):
                i_ids, t_ids, id_outputs = node.regenerate_node_ids(self.node_id, str(i))
                self.tree_ids += t_ids
                self.input_ids += i_ids
                self.id_outputs.update(id_outputs)

        return self.input_ids, self.tree_ids, self.id_outputs

    def size(self):
        """
        Recursively calculate the size of the tree

        Returns:
            Number of nodes in the tree
        """
        # Size starts at 1 to count this node
        size = 1
        for i in self.args:
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
    def __init__(self, name, args, node_id, tree_ids, input_ids, output_type, generator, static, input_types=None, value=None):
        super().__init__(name, args, node_id, tree_ids, input_ids, output_type, input_types)

        # String of the terminal value
        # This should be a python primitive (float, int, str, list, etc ...)
        # We store this as a string in memory to reduce memory usage
        # The value can always be cast into its original type
        if value is None:
            self.value = str(generator())
        else:
            self.value = value

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
        return "{}({})".format(self.name, self.value)

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
            node_ids = {curr_node_id:output_type}

            # Keep track of "x" input Terminals
            input_ids = []

            # Set the leaf nodes to be Terminal Nodes
            term_args = []
            id_counter_term = 0
            for input_type in primitive["input_types"]:
                # Choose a random terminal with the correct output type
                terminal = random.choice(terminal_set.node_set[input_type])

                # Calculate node id of this Terminal
                term_node_id = curr_node_id + str(id_counter_term)

                # Pass node_id of this Terminal if input_type is x
                input_ids_temp = [term_node_id] if input_type == "x" else []

                # Create a new TerminalNode
                term_args.append(TerminalNode(terminal["name"], 
                                         [], term_node_id, {term_node_id:input_type}, input_ids_temp,
                                         input_type, terminal["generator"], terminal["static"]))
                # Add terminal node id to the node id list
                node_ids[term_node_id] = input_type
                # Add terminal input_ids to the parent's input_ids
                input_ids += input_ids_temp
                # Increment terminal id counter so each terminal will have a different id
                id_counter_term += 1

            # Create the Node and add it to the list of children
            nodes.append(Node(primitive["name"], term_args, curr_node_id, 
                              node_ids, input_ids, output_type, primitive["input_types"]))

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
        tree_ids = {curr_node_id:output_type}
        for node in p_nodes:
            tree_ids.update(node.get_id_outputs())
        
        # Combine input_ids of children
        input_ids = []
        for node in p_nodes:
            input_ids += node.get_input_ids()
        
        # Create the Node and add it to the list of children
        nodes.append(Node(primitive["name"], p_nodes, curr_node_id, tree_ids, input_ids, output_type, primitive["input_types"]))

        # Increment id counter so each child will have a different id
        id_counter += 1

    return nodes

def generate_tree(primitive_set, terminal_set, depth=1):
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

        # Return the modified tree node
        return tree

    # This gets casted to an integer so it can be used as an index
    node_index = int(node_id[0])
    # The next node is the correct node if the length of the node_id is 1
    if len(node_id) == 1:
        next_id = ""
    else:
        next_id = node_id[1:]

    # Set the correct child to be the result of the recursion
    tree.args[node_index] = apply_at_node(modifier, primitive_set, terminal_set, tree.args[node_index], next_id)

    # Update the tree_ids and input_ids of the tree
    tree.update_tree_ids()
    tree.update_input_ids()

    return tree

def find_subtree(tree, node_id):
    """
    Recurse through the tree until the node is found
    Then return the node

    Args:
        tree: Node containing full tree
        node_id: string id directing which nodes to traverse

    Returns:
        Node containing full tree
    """
    # We have reached the correct node if the string is empty
    if node_id == "":
        # Return the tree node
        return tree

    # This gets casted to an integer so it can be used as an index
    node_index = int(node_id[0])
    # The next node is the correct node if the length of the node_id is 1
    if len(node_id) == 1:
        next_id = ""
    else:
        next_id = node_id[1:]

    # Return the recursive call
    return find_subtree(tree.args[node_index], next_id)

def parse_tree(line, pset, tset):
    """
    Parses the string of a tree
    Creates nodes from the string parsing

    Args:
        line (string): string of the tree
        pset: dictionary where (key, value) is (name, [{"output_type", "input_types", "group"}, ...])
        tset:  dictionary where (key, value) is (name, [{"output_type", "generator", "static"}, ...])
  
    Returns:
        Node containing full tree
    """
    # Controls main while loop
    parse = True
    # Stack used to keep track of created nodes
    node_stack = []
    # Stack of characters used to store node names
    node = ""
    # Current index of the character being looked at in line
    i = 0
    # Boolean for whether the last character check wass "(" or ")"
    closed = 0

    # Parse string until end of the tree is reached
    while parse:

        # Check for end of node
        if line[i] == ")":
            # Indicate last check was closed paranthesis
            closed = 1

            # Pop the stack until the item is not a Node
            pop = True
            children = []
            while pop:
                item = node_stack.pop()
                if isinstance(item, Node):
                    children.append(item)
                else:
                    name, stored_id, is_terminal = item
                    pop = False

            # Reverse children to make sure order matches original string
            children.reverse()

            if is_terminal:
                # Pass node_id of this Terminal if input_type is x
                input_ids = [stored_id] if tset[name]["output_type"] == "x" else []

                # Determine the value of the terminal
                value = "x"
                if node != "x":
                    # Assume the node is a literal (float, int, string, list, dict, etc.)
                    try:
                        value = ast.literal_eval(node)
                    except:
                        raise ValueError("Terminal value: {} Is not a Python literal".format(node))

                # Create TerminalNode and add it to node_stack
                node_stack.append(TerminalNode(name, [], stored_id, {stored_id:tset[name]["output_type"]}, input_ids,
                                         tset[name]["output_type"], tset[name]["generator"], tset[name]["static"], value=value))

            else:
                # Create full list of ids by combining the id lists of the children
                tree_ids = {stored_id:pset[name]["output_type"]}
                for node in children:
                    tree_ids.update(node.get_id_outputs())
                
                # Combine input_ids of children
                input_ids = []
                for node in children:
                    input_ids += node.get_input_ids()
                
                # Create the Node and add it to the list of children
                node_stack.append(Node(name, children, stored_id, tree_ids, input_ids, pset[name]["output_type"], pset[name]["input_types"]))

            # End of the tree
            if i == len(line) - 1:
                # Exit the while loop and return
                parse = False
                continue

            # Skip over " " and "," after returning the recursive call
            # This prevents checking the next string too early
            x = 0
            while (i+x+1 < len(line)) and (line[i+x+1] == " " or line[i+x+1] == ","):
                x += 1
            i += x

            # Reset node to empty string
            # At this point we no longer need the old string because it's already parsed
            node = ""

        # Check for start of node
        elif line[i] == "(":
            # Calculate new node_id
            if len(node_stack) == 0:
                node_id = "0"
            else:
                # Get last node id in stack
                last_node = node_stack[-1]
                if isinstance(last_node, Node):
                    stored_id = last_node.node_id
                else:
                    name, stored_id, is_terminal = last_node

                if closed:
                    # Increment last node id by 1
                    node_id = stored_id[:-1] + str(int(stored_id[-1]) + 1)
                else:
                    # Extend last node id
                    node_id = stored_id + "0"

            if node in pset:
                # Add Primitive to node_stack since we're done parsing it
                node_stack.append((node, node_id, False))
            elif node in tset:
                # Add Primitive to node_stack since we're done parsing it
                node_stack.append((node, node_id, True))
            else:
                raise Exception("Node name: {} is not in PrimitiveSet or TerminalSet".format(node))
            
            # Skip over " " and "," after returning the recursive call
            # This prevents checking the next string too early
            x = 0
            while (i+x+1 < len(line)) and (line[i+x+1] == " " or line[i+x+1] == ","):
                x += 1
            i += x

            # Reset node to empty string
            # At this point we no longer need the old string because it's already parsed
            node = ""

            # Indicate last check was open paranthesis
            closed = 0

        else:
            # Add the char to node string
            node += line[i]
   
        # Move to next character in line
        i += 1
    
    # Return the root node
    return node_stack.pop()

def check_tree_ids(tree):
    """
    Checks to make sure every node id is correct in a tree
    Used for debugging

    Args:
        tree: node containing full tree
  
    Returns:
        Node containing full tree
    """
    for i, node in enumerate(tree.args):
        if node.node_id != tree.node_id + str(i):
            import pdb; pdb.set_trace()
        check_tree_ids(node)