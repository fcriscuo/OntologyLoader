from neo4j import GraphDatabase
import os
import ast
import json

# Define the database URI, user, and password
# User and password are set as environment variables with standard Neo4j defaults
uri = "neo4j://localhost:7687"
user = os.environ.get('NEO4J_USER', "neo4j")
dimension = 4096
password = os.environ.get('NEO4J_PASSWORD', "neo4j")

# Create a driver object to connect to the database
driver = GraphDatabase.driver(uri, auth=(user, password))


#Define a function that will create a vector index for the PubMedArticle label and the embeddings property
def create_abstract_vector_index(driver) -> None:
    if index_exists("abstract-embeddings"):
        print("Vector index already exists for biolink:JournalArticle abstract embeddings")
        return
    index_query = "CALL db.index.vector.createNodeIndex('abstract-embeddings', '`biolink:JournalArticle`', 'embedding', $dimension, 'cosine')"

    driver.query(index_query, {"dimension": dimension})
    print("Created vector index for biolink:JournalArticle abstract embeddings")

def query_node_property_values(query, property_name):
    """
    Return the value of the specified property from the nodes returned by the query
    """
    with driver.session() as session:
        result = session.run(query)
        values= [record[property_name] for record in result]
        return values


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
# Delete a specified property from all nodes with a specified label
def delete_property_from_nodes(label, prop):
    """
    Delete the specified property from all nodes with the specified label
    """
    query = f"MATCH (n:{label}) REMOVE n.{prop}"
    with driver.session() as session:
        session.run(query)
    print(f"Deleted property {prop} from all nodes with label {label}")

def node_exists(label="PubMedArticle", id_prop="pub_id", id_value=0):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value
        query = f"MATCH (n:{label}) WHERE n.{id_prop} = {format_neo4j_property_value(id_value)} RETURN n"
        # Run the query with the parameters
        result = session.run(query, id_value=id_value)
        # Return True if the result contains a record
        return result.single() is not None

def is_numeric(value):
  """Checks if a value is numeric (int or float)."""
  return isinstance(value, (int, float))

def needs_properties_nodes_exist():
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Constrct a Neo4j query that detemines if there are any PubMedArticle nodes that have the needs_properties property set to TRUE
        query = "MATCH (n:`biolink:JournalArticle`) WHERE n.needs_properties = TRUE RETURN COUNT(n) > 0 AS result"
        # Run the query with the parameters
        result = session.run(query)
        # Return True if the result contains a record
        return result.single() is not None

def is_list_value(data, key):
  return isinstance(data.get(key), list)

# Define a function that takes a node label, an identifier property, an identifier value,
# and a dictionary of new properties as arguments and updates the node in the database
def update_node(label, id_prop, id_value, properties):
    """
    Update the specified node with the specified properties
    """
    if not node_exists(label, id_prop, id_value):
        print(f"Node for {label} {id_prop} {id_value} does not exist.")
        return
    query = f"MATCH (n:{label} {{{id_prop}: {format_neo4j_property_value(id_value)}}}) SET "
    for key in properties:
        if is_numeric(properties[key]) or is_list_value(properties, key):
            query += f"n.{key} = {properties[key]}, "
        else :
             query += f"n.{key} = '{properties[key]}', "
    query = query[:-2]
    with driver.session() as session:
        try:
            session.run(query)
            print(f"Updated node {label} {id_prop} {id_value}")
        except Exception as e:
            print(f"Error updating node {label} {id_prop} {id_value}: {e}")

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
def convert_selected_properties_to_neo4j_list(data, keys):
    """
    Processes a dictionary by applying a function to specific keys and values.
    Primary intent is to convert a list of strings to a list of quoted strings for use in a Cypher query.

    Args:
        data: The original dictionary.
        keys: A list of keys to process.

    Returns:
        A new dictionary with the processed values.
    """
    new_data = {}
    for key, value in data.items():
        if key in keys:
            new_data[key] = parse_to_quoted_neo4j_string_list(value)
        else:
            new_data[key] = value
    return new_data


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

# define a function that accepts a string representing a Neo4j array and returns a list of strings
def neo4j_array_to_list(neo4j_array:str):
    data = json.loads(neo4j_array)
    return data

# define a function that accepts a string as an neo4j index name
# and returns true if that index exists
def index_exists(index_name):
    with driver.session() as session:
        query = f"show indexes YIELD name WHERE name = '{index_name}' RETURN name"
        result = session.run(query)
        return result.single() is not None
# Function to remove single quotes from a string
# prevents parsing errors in Cypher queries
def remove_single_quotes(input_string):
  """Removes single quotes from a string.

  Args:
      input_string: The string to modify.

  Returns:
      The modified string with single quotes removed.
  """
  if "'" in input_string:
    return input_string.replace("'", "")
  else:
    return input_string

def edit_biological_string(input_string):
  """Edits a string for biological notations.

  Args:
      input_string: The input string.

  Returns:
      The edited string.
  """
  # Specific replacements for greater efficiency
  edited_string = input_string.replace("3'", "3-prime").replace("5'", "5-prime")

  # Replace other single quotes with blanks
  for char in edited_string:
    if char == "'":
        edited_string = edited_string.replace(char, "")

  return edited_string
