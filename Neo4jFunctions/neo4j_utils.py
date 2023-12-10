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
    query = f"MATCH (n:{label} {{{id_prop}: {id_value}}}) RETURN n.{prop}"
    with driver.session() as session:
        result = session.run(query)
        value = result.single()[0]
        return value

def node_exists(label="PubMedArticle", id_prop="pub_id", id_value=0):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value
        query = f"MATCH (n:{label}) WHERE n.{id_prop} = {id_value} RETURN n"
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
    query = f"MATCH (n:{label} {{{id_prop}: {id_value}}}) SET "
    for key in properties:
        query += f"n.{key} = '{properties[key]}', "
    query = query[:-2]
    with driver.session() as session:
        session.run(query)