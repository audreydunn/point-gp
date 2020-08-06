"""
This file contains objects used to store Node information
Each primitive and terminal is unique
"""
from copy import deepcopy

class NodeSet():
    def __init__(self):
        # Stores all of the node set information
        self.node_set = {}
        self.function_pointers = {}

    def struct_by_name(self):
        """
        Restructures node_set to make "name" the main key
        Copies over the remaining key->value pairs
        """
        new_dict = {}
        for output_type in self.node_set:
            for i in range(len(self.node_set[output_type])):
                # Set the new key to be the name and store the output_type
                new_dict[self.node_set[output_type][i]["name"]] = {"output_type":output_type}
                # Copy the remaining key->value pairs
                for key in self.node_set[output_type][i]:
                    if key != "name":
                        new_dict[self.node_set[output_type][i]["name"]][key] = self.node_set[output_type][i][key]

        return new_dict

    def __add__(self, other):
        """
        Addtion operator for adding node_sets
        """
        # Make sure the types are matching
        if not isinstance(other, type(self)):
            raise TypeError("unsupported operand type(s) for +: {} and {}".format(type(self), type(other)))

        # Make a deepcopy of self to make sure the original NodeSet is not modified
        new_set = deepcopy(self)

        # Add function_pointers together
        new_set.function_pointers.update(other.function_pointers)

        # Combine the node_sets
        # If dict.update(other_dict) is used instead then 
        # the primitives with the same output types in self.node_set 
        # will be replaced with the primitives of the same output type in other.node_set
        for output_type in other.node_set:
            if output_type in self.node_set:
                new_set.node_set[output_type] += other.node_set[output_type]
            else:
                new_set.node_set[output_type] = other.node_set[output_type]

        return new_set

    def __radd__(self, other):
        """
        Reverse Add for adding node_sets

        This is needed for sum() to work on NodeSet objects
        """
        if other == 0:
            return deepcopy(self)
        else:
            return self.__add__(other)

    def __str__(self):
        """
        String representation of NodeSet

        Returns:
            string of self.node_set dictionary
        """
        return str(self.node_set)

class PrimitiveSet(NodeSet):
    def __init__(self):
        super().__init__()

    def add_primitive(self, func, output_type, name, input_types, group):
        """
        Stores relevant primitive information into the primitive set

        Args:
            output_type: string of the output type
            name: unique string of the primitive
            input_types: list of type strings for each input into the primitive
            group: string used to group primitives together

        """
        # Make sure primitive name is unique
        # Inefficent search but primitives are only added
        # before the optimization so the memory saved is worth it
        found_name = False
        for key in self.node_set:
            for primitive in self.node_set[key]:
                if primitive["name"] == name:
                    found_name = True
                    break

        # Raise error if primitive name already exists
        if found_name:
            raise Exception("Primitive Name: {} Already Exists".format(name))

        # Set primitive name to point to its function
        # If a primitive wrapper is implemented, then this code needs to be modified
        self.function_pointers[name] = func

        # Check if the output_type is not already in the primitive set
        if output_type not in self.node_set:
            # Create output_type list
            self.node_set[output_type] = []
        
        # Add the primitive information
        self.node_set[output_type].append({"name": name, "input_types": input_types, "group": group})

class TerminalSet(NodeSet):
    def __init__(self):
       super().__init__()

    def add_terminal(self, output_type, name, generator, static):
        """
        Stores relevant terminal information into the terminal set

        Args:
            output_type: string of the output type
            name: unique string of the primitive
            generator: function that generates the output type
            static: determines whether mutating changes terminal types

        """
        # Make sure terminal name is unique
        # Inefficent search but terminals are only added
        # before the optimization so the memory saved is worth it
        found_name = False
        for key in self.node_set:
            for terminal in self.node_set[key]:
                if terminal["name"] == name:
                    found_name = True
                    break

        # Raise error if terminal name already exists
        if found_name:
            raise Exception("Terminal Name: {} Already Exists".format(name))

        # Raise error if static is not a Boolean
        if not isinstance(static, bool):
            raise Exception("static variable must be a Boolean: True/False.")

        # Check if the output_type is not already in the terminal set
        if output_type not in self.node_set:
            # Create output_type list
            self.node_set[output_type] = []

        # Set terminal name to point to a lambda function that returns its value
        # If a terminal wrapper is implemented, then this code needs to be modified
        self.function_pointers[name] = lambda value: value
        
        # Add the terminal information
        self.node_set[output_type].append({"name": name, "generator": generator, "static": static})