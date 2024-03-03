import os

from neo4j import GraphDatabase

import PubMedReferenceImporter as pri

"""
A collection of Python functions to interact with a Neo4j database
n.b. Code development assisted by Github Copilot
Author: Fred Criscuolo
"""

# Define the database URI, user, and password
# User and password are set as environment variables with standard Neo4j defaults
uri = "neo4j://localhost:7687"
user = os.environ.get('NEO4J_USER', "neo4j")
dimension = 4096
password = os.environ.get('NEO4J_PASSWORD', "neo4j")

# Create a driver object to connect to the database
driver = GraphDatabase.driver(uri, auth=(user, password))


# Define a function that will define a constraint for the `biolink:JournalArticle` label and the pub_id property
# This constraint will ensure that the pub_id property is unique
def create_journal_article_id_constraint():
    with driver.session() as session:
        session.run(
            "CREATE CONSTRAINT unique_journal_article_id IF NOT EXISTS FOR (article:`biolink:JournalArticle`) REQUIRE article.id IS UNIQUE")
        session.close()
        print("Created `biolink:JournalArticle` ID constraint")
        create_vector_index(driver)


# Define a function that will create a vector index for the `biolink:JournalArticle` label and the embeddings property
def create_vector_index(driver) -> None:
    index_query = "CALL db.index.vector.createNodeIndex('`biolink:JournalArticle`', '`biolink:JournalArticle`', 'embeddings', $dimension, 'cosine')"
    try:
        driver.query(index_query, {"dimension": dimension})
        print("Created vector index for `biolink:JournalArticle` embeddings")
    except:  # Already exists
        print(f"Vector index already exists for `biolink:JournalArticle` embeddings")
        pass

# Define a function that takes a query as an argument and returns a list of nodes

def get_nodes(query):
    with driver.session() as session:
        result = session.run(query)
        nodes = [record.values()[0] for record in result]
    return nodes


# Define a function that takes a node label, an identifier property, an identifier value, and a property name as arguments and returns the value of the property
def get_node_property(label, id_prop, id_value, prop):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value, and returns the value of the property
        query = f"MATCH (n:{label}) WHERE n.{id_prop} = {id_value} RETURN n.{prop} as {prop}"
        # Run the query with the parameters
        result = session.run(query, id_value=id_value)
        # Return the property value
        record = result.single()
        return record[prop] if record is not None else None


# Define a function that takes a node label, an identifier property, an identifier value, 
# and a dictionary of new properties as arguments and updates the node in the database
def update_node(label, id_prop, id_value, props):
    # print(f"PubMedNeo4jFunctions: update_node {label} {id_prop} {id_value}")
    # confirm that the node exists
    if not node_exists(label, id_prop, id_value):
        print(f"Node for {label} {id_prop} {id_value} does not exist.")
        return
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value, and sets the new properties
        query = f"MATCH (n:{label}) WHERE n.{id_prop} = {id_value} SET n += $props"
        # Run the query with the parameters
        session.run(query, id_value=id_value, props=props)
        session.close()
        references = props["references"]
        # print(f"procsessing references {references}")
        if references is not None:
            create_reference_nodes(id_value, references)
            # print(f"processing references for {id_value} {references}")
            pri.persist_reference_data(id_value, references)


# Define a function that will set the embeddings property for a specified `biolink:JournalArticle` node
def set_embeddings_property(pmid, embeddings):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value, and sets the new properties
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = PMID:{pmid} SET n.embeddings = $embeddings"
        # Run the query with the parameters
        session.run(query, id_value=pmid, embeddings=embeddings)
        session.close()


# Define a function that will create placholder nodes for the references
def create_reference_nodes(pub_id, reference_ids):
    [create_reference_node(pub_id, reference_id) for reference_id in reference_ids]


# Define a function tha will create a Reference node and a relationship to an existing PubMed node
def create_reference_node(pub_id, reference_id):
    # Initialize an empty dictionary to store the properties
    props = {}
    parent_id = f"PMID:{pub_id}"
    child_id = f"PMID:{reference_id}"

    # Set the reference ID property
    props["id"] = child_id

    # Set the needs_properties property
    props["needs_properties"] = True

    # Set the needs_references property
    props["needs_references"] = False
    
    # Set the category property
    props["category"] = ["`biolink:Entity`",
        "`biolink:NamedThing`",
        "`biolink:InformationContentEntity`",
        "`biolink:Publication`",
        "`biolink:Article`",
        "`biolink:JournalArticle`"]
    #Set the iri property
    props["iri"] = f"https://pubmed.ncbi.nlm.nih.gov/{reference_id}"
 
    # Create the Reference node
    if not node_exists("`biolink:JournalArticle`", "id", child_id):
        print(f"Creating `biolink:JournalArticle` (reference) node for {child_id}")
        create_node(":`biolink:Entity`:`biolink:NamedThing`:`biolink:InformationContentEntity`:`biolink:Publication`:`biolink:Article`:`biolink:JournalArticle`", props)
    # Create the relationship
    create_relationship("`biolink:JournalArticle`", "id", parent_id,
                        "`biolink:JournalArticle`", "id", child_id, "CITES")
    negate_needs_references_property(parent_id)


# Define a function to determine if a node exists in the database
# default id_prop is id
# default labe is `biolink:JournalArticle`
# default id_value is PMID:0

def node_exists(label="`biolink:JournalArticle`", id_prop="id", id_value="PMID:0"):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value
        query = f"MATCH (n:{label}) WHERE n.{id_prop} = {id_value} RETURN n"
        # Run the query with the parameters
        result = session.run(query, id_value=id_value)
        # Return True if the result contains a record
        return result.single() is not None


# Define a function to determine if a `biolink:JournalArticle` node's needs_references is FALSE

def needs_references_nodes_exist(pmid):
    # Use a context manager to create a session with the driver
    id = f"PMID:{pmid}"
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value
        if node_exists("`biolink:JournalArticle`", "id", id):
            query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} RETURN n.needs_references as exists"
            # Run the query with the parameters
            result = session.run(query, id_value=pmid)
            record = result.single()
            return record is not None and record["exists"] is True
        else:
            return False


def create_relationship(label1, id_prop1, id_value1, label2, id_prop2, id_value2, rel_type):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the nodes by label and identifier property and value, and creates a relationship between them
        query = f"MATCH (n1:{label1} {{{id_prop1}: {id_value1}}}), (n2:{label2} {{{id_prop2}: {id_value2}}}) MERGE (n1)-[:{rel_type}]->(n2)"
        # Run the query with the parameters
        session.run(query, id_value1=id_value1, id_value2=id_value2)


def create_node(label, props):
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that creates a node with the given label and properties
        query = f"CREATE (n:{label} $props)"
        # Run the query with the parameter
        session.run(query, props=props)


def node_has_label(pub_id, label):
    # Use a context manager to create a session with the driver
    id = f"PMID:{pub_id}"
    with driver.session() as session:
        # Construct a query that matches the `biolink:JournalArticle` node and pub_id and adds the label
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} AND n:{label} RETURN TRUE AS exists"
        # Run the query with the parameter
        result = session.run(query, id=id)
        # Return True if the result contains a record
        record = result.single()
        exists = bool(record["exists"]) if record is not None else False
        return exists


# Define a function that takes a node id and a label as arguments and adds the label to the node in the database

def add_label(pub_id, label):
    id = f"PMID:{pub_id}"
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # determine if the node already has this label
        if node_has_label(pub_id, label):
            print(f"Node {pub_id} already has label {label}.")
            return
        # Construct a query that matches the `biolink:JournalArticle` node and pub_id and adds the label
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} SET n:{label}"
        # Run the query with the parameter
        session.run(query, id=id)
        print(f"Added label {label} to node {id}")


# Define a function that will set the embeddings property for a specified `biolink:JournalArticle` node
def set_embeddings_property(pub_id, embeddings):
    id = f"PMID:{pub_id}"
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value, and sets the new properties
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} SET n.embeddings = $embeddings"
        # Run the query with the parameters
        session.run(query, id_value=id, embeddings=embeddings)
        session.close()

# Define a function to detach and delete a `biolink:JournalArticle` node based on its PubMed ID

def delete_journal_article_nodes(pub_id):
    id = f"PMID:{pub_id}"
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that detaches and deletes the node by label and identifier property and value
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} DETACH DELETE n"

        # Run the query with the parameters
        session.run(query, id_value=id)
        print(f"Deleted JournalArticle ID: {id}")

# set the needs_references property to FALSE for a `biolink:JournalArticle` node
def negate_needs_references_property(pub_id):
    id = f"PMID:{pub_id}"
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value, and sets the new properties
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} SET n.needs_references = FALSE"
        # Run the query with the parameters
        session.run(query, id_value=id)
        session.close()

    # Define a function that will set the needs_proerties property and the needs_references property to FALSE for a `biolink:JournalArticle` node


# If a placeholder`biolink:JournalArticle` node represents a book rather than a journal article,
# the needs_properties property will be set to FALSE
# This prevents the node from being selected for processing
# The needs_references property will also be set to FALSE to prevent the node from being selected
# for processing
def negate_needs_props_and_refs(pub_id):
    id = f"PMID:{pub_id}"
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value, and sets the new properties
        query = f"MATCH (n:`biolink:JournalArticle`) WHERE n.id = {id} SET n.needs_properties = FALSE, n.needs_references = FALSE"
        # Run the query with the parameters
        session.run(query, id_value=id)
        session.close()
        print(f"Turned off properties flags for JournalArticle ID: {id}")

    # Define a function that will determine if there are any nodes in the database that have the needs_properties property set to TRUE

# This function is used by the BatchPubMedDataImporter.py script to determine if there are any nodes that need to be processed
def needs_properties_nodes_exist():
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Constrct a Neo4j query that detemines if there are any `biolink:JournalArticle` nodes that have the needs_properties property set to TRUE
        query = "MATCH (n:`biolink:JournalArticle`) WHERE n.needs_properties = TRUE RETURN COUNT(n) > 0 AS result"
        # Run the query with the parameters
        result = session.run(query)
        # Return True if the result contains a record
        return result.single() is not None


# define a function that detertmines if there are any `biolink:JournalArticle` nodes in the database where the embeddings property is null
def needs_embeddiings_nodes_exist():
    # Use a context manager to create a session with the driver
    with driver.session() as session:
        # Construct a query that matches the node by label and identifier property and value
        query = ("MATCH (p:`biolink:JournalArticle`) WHERE p.abstract IS NOT NULL AND"
                 " p.abstract <> '' AND p.embeddings IS NULL RETURN COUNT(p) > 0 AS result")
        # Run the query with the parameters
        result = session.run(query)
        # Return True if the result contains a record
        return result.single() is not None