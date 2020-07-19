from tree import generate_tree
import random

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
                    "x": [{"name": "original_input", "generator": lambda: "x"}]
                   }

    tree = generate_tree(primitive_set, terminal_set, depth=4)
    print("Tree String:\n{}\n".format(str(tree)))
    node_ids = tree.get_id_list()
    print("Unique Node IDs:\n{}\n".format(node_ids))
    print("Number of Unique Node IDs:\n{}\n".format(len(node_ids)))
    print("Tree Size (Number of Nodes):\n{}\n".format(tree.size()))
    # TODO: Create functions for the primitives, so tree.compile() can be tested