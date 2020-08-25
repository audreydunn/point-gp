"""
A Tree consists of one root Node linking down to every other node

Tree gets compiled top down
"""
from copy import deepcopy
import random
import ast

class Tree():
    def __init__(self, nodes, root="0"):
        # Dictionary with format (node_id -> Node)
        self.nodes = nodes

        # node_id of the root node
        self.root = root

    def get_tree_ids(self):
        """
        Get list of ids

        Returns:
            List containing the ids of every node in the tree
        """
        return list(self.nodes.keys())

    def get_input_ids(self):
        """
        Get list of ids
        Where each id is a terminal node with output_type "x"

        Returns:
            List containing the ids of every terminal node with output_type "x" in the tree
        """
        return [key for key in self.nodes if len(self.nodes[key].children) == 0 and self.nodes[key].output_type == "x"]

    def get_terminal_ids(self):
        """
        Get list of ids
        Where each id is a terminal node

        Returns:
            List containing the ids of every terminal node
        """
        return [key for key in self.nodes if len(self.nodes[key].children) == 0]

    def remove(self, node_id):
        """
        Removes a subtree from a tree

        Args:
            node_id: id of a node in this tree's node dictionary
        """
        # Call this function again on every child
        for child in self.nodes[node_id].children:
            self.remove(child)

        # Remove node from the tree
        del self.nodes[node_id]

    def get_subtree(self, node_id):
        """
        Creates a subtree with node_id as the root

        Args:
            node_id: id of a node in this tree's node dictionary

        Returns:
            new Tree object of a subtree with node_id as the root
        """
        return Tree(self.subtree_recurse(node_id), node_id)

    def subtree_recurse(self, node_id):
        """
        Recursively creates a new dictionary of nodes
        starting with node_id as the root 

        Args:
            node_id: id of a node in this tree's node dictionary

        Returns:
            dictionary of all the nodes in the subtree
        """
        temp_nodes = {node_id:deepcopy(self.nodes[node_id])}
        
        # Recursive call on every child
        for child in self.nodes[node_id].children:
            temp_nodes.update(self.subtree_recurse(child))

        return temp_nodes

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

    def size(self):
        """
        Returns number of nodes in the tree

        Returns:
            Number of nodes in the tree
        """
        return len(self.nodes)

    def regenerate_recurse(self, curr_node_id, new_node_id, position, new_nodes):
        """
        Recursively updates all of the node ids of the tree
        Starting from the given node_id

        Args:
            curr_node_id: node_id in the existing tree
            new_node_id: root node_id of the new tree
            position: string corresponding to the position of the node under the root
            new_nodes: temporary nodes dictionary used to prevent overwriting the existing nodes
        """
        # list for new child ids
        child_ids = []

        # Replace the old node_id with the new one. Set the value to be the old Node
        new_nodes[new_node_id + position] = self.nodes.pop(curr_node_id, None)

        # Debug
        if new_nodes[new_node_id + position] is None:
            raise Exception("curr_node_id is not in self.nodes")

        # Recursive Call on children
        for i, node in enumerate(new_nodes[new_node_id + position].children):
            self.regenerate_recurse(node, new_node_id + position, str(i), new_nodes)
            child_ids.append(new_node_id + position + str(i))

        # Correct child ids
        new_nodes[new_node_id + position].children = child_ids

    def regenerate_node_ids(self, new_node_id, position):
        """
        Recursively updates all of the node ids of the tree
        Starting from the given node_id

        Args:
            node_id: new starting node_id of the tree
            position: string corresponding to the position of the node under the root
        """
        new_nodes = {}
        self.regenerate_recurse(self.root, new_node_id, position, new_nodes)
        self.nodes = new_nodes
        self.root = new_node_id

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

    def create_lisp(self, node_id):
        """
        Recursively converts the tree into a string of function calls
        Based on LISP https://en.wikipedia.org/wiki/Lisp_(programming_language)

        Args:
            node_id: new starting node_id of the tree

        Returns:
            LISP string representation of the tree
        """
        # If Terminal Node
        if len(self.nodes[node_id].children) == 0:
            return "{}({})".format(self.nodes[node_id].name, self.nodes[node_id].value)
        return self.nodes[node_id].name + "(" + "".join([self.create_lisp(i) + ", " for i in self.nodes[node_id].children])[:-2] + ")"

    def __str__(self):
        """
        Recursively converts the tree into a string of function calls
        Based on LISP https://en.wikipedia.org/wiki/Lisp_(programming_language)

        Starts from the root node

        Returns:
            LISP string representation of the tree
        """
        return self.create_lisp(self.root)
    

class Node():
    def __init__(self, name, children, output_type, input_types):
        
        # 0 .. N children nodes. Leaves have 0 children
        # example args: [child_1, child_2, ... , child_n]
        self.children = children

        # string primitive name
        # example: math.sin
        self.name = name

        # Data type of the node
        # This is the output type
        self.output_type = output_type

        # Input types of the node
        # Used for evolutionary operators
        self.input_types = input_types

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
        Shows the name and input types of the Node

        Returns:
            string representation of the non-terminal Node
        """
        return "{}({})".format(self.name, self.input_types)

class TerminalNode(Node):
    def __init__(self, name, children, output_type, generator, static, value=None, input_types=None):
        super().__init__(name, children, output_type, input_types)

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
        Shows the name and value of the TerminalNode

        Returns:
            string representation of the TerminalNode
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
        Dictionary of nodes in the tree
    """
    # Dictionary of child nodes
    nodes = {}
    # Ids of the children generated by this recursion
    child_ids = []
    # Use to differentiate ids
    id_counter = 0

    # Leaf node
    if depth == 1:
        for output_type in output_types:
            # Select a random primitive with the correct output type
            primitive = random.choice(primitive_set.node_set[output_type])

            # Create current node_id
            curr_node_id = node_id + str(id_counter)

            # Add current node_id to child_ids
            child_ids.append(curr_node_id)

            # Set the leaf nodes to be Terminal Nodes
            id_counter_term = 0
            term_child_ids = []
            for input_type in primitive["input_types"]:
                # Choose a random terminal with the correct output type
                terminal = random.choice(terminal_set.node_set[input_type])

                # Calculate node id of this Terminal
                term_node_id = curr_node_id + str(id_counter_term)

                # Create a new TerminalNode
                nodes[term_node_id] = TerminalNode(terminal["name"], [], input_type, 
                                                   terminal["generator"], terminal["static"])

                # Add the terminal id to the terminal child id list
                term_child_ids.append(term_node_id)

                # Increment terminal id counter so each terminal will have a different id
                id_counter_term += 1

            # Create the Node and add it to the list of children
            nodes[curr_node_id] = Node(primitive["name"], term_child_ids,
                                       output_type, primitive["input_types"])

            # Increment id counter so each child will have a different id
            id_counter += 1
        
        return nodes, child_ids

    # All other nodes
    for output_type in output_types:
        # Select a random primitive with the correct output type
        primitive = random.choice(primitive_set.node_set[output_type])

        # Create current node_id
        curr_node_id = node_id + str(id_counter)

        # Generate children nodes
        # One for each input type
        p_nodes, p_child_ids = generate(primitive_set, terminal_set, depth-1, primitive["input_types"], curr_node_id)

        # Add p_nodes to the nodes dictionary
        nodes.update(p_nodes)
        
        # Create the Node and add it children dictionary
        nodes[curr_node_id] = Node(primitive["name"], p_child_ids, output_type, primitive["input_types"])

        # Add current node_id to list of child ids
        child_ids.append(curr_node_id)

        # Increment id counter so each child will have a different id
        id_counter += 1

    return nodes, child_ids

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

    # Generate tree
    nodes, child_ids = generate(primitive_set, terminal_set, depth, ["x"], "")
    return Tree(nodes)

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

def check_tree_ids(tree, node_id):
    """
    Checks to make sure every node id is correct in a tree
    Used for debugging

    Args:
        tree: tree object containing nodes
        node_id: id of the node to search
    """
    for i, node in enumerate(tree.nodes[node_id].children):
        if node != node_id + str(i):
            import pdb; pdb.set_trace()
        check_tree_ids(tree, node)