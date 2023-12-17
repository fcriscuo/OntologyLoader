from neo4j import GraphDatabase
import os

# Define the database URI, user, and password
# User and password are set as environment variables with standard Neo4j defaults
uri = "neo4j://localhost:7687"
user = os.environ.get('NEO4J_USER', "neo4j")
dimension = 4096
password = os.environ.get('NEO4J_PASSWORD', "neo4j")

# Create a driver object to connect to the database
driver = GraphDatabase.driver(uri, auth=(user, password))

# Define a function that takes a query as an argument and returns a list of nodes
def get_nodes(query):
    """
    Execute the query and return the result as a list of nodes
    """
    with driver.session() as session:
        result = session.run(query)
        nodes = [record["n"] for record in result]
        return nodes

# Define a function that takes a node label, an identifier property, an identifier value, and a property name as arguments and returns the value of the property
def get_node_property(label, id_prop, id_value, prop):
    """
    Return the value of the specified property for the specified node
    """
    query = f"MATCH (n:{label} {{{id_prop}: {format_neo4j_property_value(id_value)}}}) RETURN n.{prop}"
    with driver.session() as session:
        result = session.run(query)
        value = result.single()[0]
        return value

def node_exists(label="PubMedArticle", id_prop="pub_id", id_value=0):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value
        query = f"MATCH (n:{label}) WHERE n.{id_prop} = {format_neo4j_property_value(id_value)} RETURN n"
        # Run the query with the parameters
        result = session.run(query, id_value=id_value)
        # Return True if the result contains a record
        return result.single() is not None

# Define a function that takes a node label, an identifier property, an identifier value, and a dictionary of new properties as arguments and updates the node in the database
def update_node(label, id_prop, id_value, properties):
    """
    Update the specified node with the specified properties
    """
    if not node_exists(label, id_prop, id_value):
        print(f"Node for {label} {id_prop} {id_value} does not exist.")
        return
    query = f"MATCH (n:{label} {{{id_prop}: {format_neo4j_property_value(id_value)}}}) SET "
    for key in properties:
        query += f"n.{key} = '{properties[key]}', "
    query = query[:-2]
    with driver.session() as session:
        session.run(query)


# Define a function entitled format_neo4j_property_value, that takes a string.
# If the string is enclosed in double quotes and its value is a number, remove the double quotes,
# otherwise return the string as is. The return value, numeric or not, is still a string.
# The string '"ABC"' is returned as '"ABC"'
# The string '"123"' is returned as '123'

def format_neo4j_property_value(value):
    """
    Format a Neo4j property value
    """
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if value.isnumeric():
            return value
    else:
        return f'"{value}"'


# define a function that accepts a double-quoted and if numeric returns it as an integer
# If the string value is not a valid integer, return 0

def format_neo4j_property_value_as_int(value):
    """
    Format a Neo4j property value as an integer
    """
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
        if value.isnumeric():
            return int(value)
        else:
            return 0
    else:
        return int(value)

#Specialized function that encapsulates all members of a delimited String
# as quoted Strings in a list
#Necessary for delimited Strings that may contain numeric values
#Neo4j cannot process arrays with mixed members
def parse_to_quoted_neo4j_string_list(string, sep='|'):
    if string:
        list_ = [f'"{symbol}"' for symbol in string.split(sep)]
        return f"[{', '.join(list_)}]"
    else:
        return "[]"