from Neo4jFunctions import neo4j_utils as nju
from ontology_model.obo_model import OboTerm

# define a function that takes an OntologyTerm object and determines if a node labeled as OntologyTerm exists in the database based on the OntologyTerm's id property

def ontology_term_exists(obt):
    """
    Return True if a node labeled as OntologyTerm exists in the database based on the OntologyTerm's id property
    """
    return nju.node_exists("OntologyTerm", "id", obt.id)


# define a function that takes an OntologyTerm object, and based on the OntologyTerm's id queries if an OntologyTerm node exists in the database, if not it creates an OntologyTerm node in the database

def create_or_update_OntologyTerm_node(obt: OboTerm):
    """
    Create or update an OntologyTerm node in the database
    """
    if not ontology_term_exists(obt):
        query = f"CREATE (n:OntologyTerm {{id: '{obt.id}', name: '{obt.term_name}', namespace: '{obt.namespace}', def: '{obt.definition}'}})"
        with nju.driver.session() as session:
            session.run(query)
    else:
        query = f"MATCH (n:OntologyTerm {{id: '{obt.id}'}}) SET n.name = '{obt.term_name}', n.namespace = '{obt.namespace}', n.def = '{obt.definition}'"
        with nju.driver.session() as session:
            session.run(query)
    # If the OntologyTerm has synonyms, create or update the OntologyTerm node with an Array of synonyms
    if obt.synonyms:
        process_OntologyTerm_synonyms(obt)
    # If the OntologyTerm has pmids, process the pmids
    if obt.pmids:
        process_OntologyTerm_pmids(obt)
    if obt.relationships:
        process_OntologyTerm_relationships(obt)
    if obt.xrefs:
        process_OntologyTerm_xrefs(obt)
    # Use the OntologyTerm's ontology_name property to add a label to the OntologyTerm node
    if obt.ontology_name:
        query = f"MATCH (n:OntologyTerm {{id: '{obt.id}'}}) SET n:{obt.ontology_name.replace(' ','_')}"
        with nju.driver.session() as session:
            session.run(query)


    # define a function that takes an PubMedArticle object and determines if a node labeled as PubMedArticle exists in the database based on the PubMedArticle's pub_id property

def pubmed_article_node_exists(pub_id:int):
    """
    Return True if a node labeled as PubMedArticle exists in the database based on the PubMedArticle's pub_id property
    """
    return nju.node_exists("PubMedArticle", "pub_id", str(pub_id))

# define a function that processes a List of integers as PubMedArticle pub_ids, if a PubMedArticle node does not exist in the database for the pub_id, it creates a PubMedArticle node in the database
# set the new PubMedArticle node's needs_properties property to True and tne needs_references property to True.
# Only set the pubmed_id property if the pub_id is not None
# If the PubMedArticle node exists in the database, do nothing

def create_or_update_pubmed_article_node(pubmed_ids):
    """
    Create or update a PubMedArticle node in the database
    """
    for pubmed_id in pubmed_ids:
        if not pubmed_article_node_exists(pubmed_id):
            query = f"CREATE (n:PubMedArticle {{pub_id: {str(pubmed_id)}, needs_properties: TRUE, needs_references: TRUE}})"
            with nju.driver.session() as session:
                session.run(query)
        else:
            continue

# define a function that takes an OntologyTerm object and a PubMedArticle object as arguments and creates a relationship between the OntologyTerm and PubMedArticle nodes in the database

def create_OntologyTerm_pubmed_article_relationship(obt, pub_id:int):
    """
    Create a relationship between the OntologyTerm and PubMedArticle nodes in the database
    """
    query = f"MATCH (o:OntologyTerm {{id: '{obt.id}'}}), (p:PubMedArticle {{pub_id: {str(pub_id)}}}) CREATE (o)-[:CITES]->(p)"
    with nju.driver.session() as session:
        session.run(query)

# define a function that takes an OntologyTerm object and processes its List of  pmids
# for each pubmed_id in the List of pmids, create a PubMedArticle node in the database if it does not exist
# and create a relationship between the OntologyTerm and PubMedArticle nodes in the database

def process_OntologyTerm_pmids(obt):
    """
    Create PubMedArticle nodes and relationships between the OntologyTerm and PubMedArticle nodes in the database
    """
    for pubmed_id in obt.pmids:
        create_or_update_pubmed_article_node([pubmed_id])
        create_OntologyTerm_pubmed_article_relationship(obt, pubmed_id)

#Process OboTerm xrefs
# define a function that takes a List of OboXref objects and for each OboXref object,
# maps that OboXref object to an OboTerm object. If the new OboTerm object does not exist in the database as an OntologyTerm node,
# create an OntologyTerm node in the database using the new OboTerm object
# Create a relationship between the first OntologyTerm node and the second OntologyTerm node in the database.
# The relationship between the OntologyTerm and OntologyTerm nodes is labeled as HAS_XREF

# Process intra-ontology relationships

# define a function that takes an OboTerm object and processes its List of relationships
# for each OboRelationship object in the List of relationships, create an OboTerm object using the OboRelationship's id and term_name properties
# if the new OboTerm object does not exist in the database as an OntologyTerm node, create an OntologyTerm node in the database using the new OboTerm object
# create a relationship between the first OntologyTerm node and the second OntologyTerm node in the database.
# use the OboRelationship's type property as the relationship label

def process_OntologyTerm_relationships(obt):
    """
    Create OntologyTerm nodes and relationships between the OntologyTerm and OntologyTerm nodes in the database
    """
    for relationship in obt.relationships:
        # map the OboRelationship object to an OboTerm object
        obo_term = OboTerm(relationship.id, relationship.term_name)
        # if the OboTerm object does not exist in the database as an OntologyTerm node, create an OntologyTerm node in the database using the new OboTerm object
        if not ontology_term_exists(obo_term):
            create_or_update_OntologyTerm_node(obo_term)
        # create a relationship between the first OntologyTerm node and the second OntologyTerm node in the database.
        # use the OboRelationship's type property as the relationship label
        query = f"MATCH (o1:OntologyTerm {{id: '{obt.id}'}}), (o2:OntologyTerm {{id: '{obo_term.id}'}}) CREATE (o1)-[:{relationship.type}]->(o2)"
        with nju.driver.session() as session:
            session.run(query)
def process_OntologyTerm_xrefs(obt):
    """
    Create OntologyTerm nodes and relationships between the OntologyTerm and OntologyTerm nodes in the database
    """
    for xref in obt.xrefs:
        # map the OboXref object to an OboTerm object
        obo_term = OboTerm(xref.term_id, xref.name)
        # if the OboTerm object does not exist in the database as an OntologyTerm node, create an OntologyTerm node in the database using the new OboTerm object
        if not ontology_term_exists(obo_term):
            create_or_update_OntologyTerm_node(obo_term)
        # create a relationship between the first OntologyTerm node and the second OntologyTerm node in the database.
        # The relationship between the OntologyTerm and OntologyTerm nodes is labeled as HAS_XREF
        query = f"MATCH (o1:OntologyTerm {{id: '{obt.id}'}}), (o2:OntologyTerm {{id: '{obo_term.id}'}}) CREATE (o1)-[:HAS_XREF]->(o2)"
        with nju.driver.session() as session:
            session.run(query)



#Process Synonyms
# define a function that takes a List of OboSynonym objects and for each OboSynonym object,
# creates a node in the database if it does not exist and creates a relationship
# between the OntologyTerm and OboSynonym nodes in the database.
# The relationship between the OntologyTerm and OboSynonym nodes is labeled as HAS_SYNONYM
# and has a relationship property that is derived from the OboSynonym's type property


def process_OntologyTerm_synonyms(obt):
    """
    Create OboSynonym nodes and relationships between the OntologyTerm and OboSynonym nodes in the database
    """
    for synonym in obt.synonyms:
        if not nju.node_exists("OboSynonym", "name", synonym.synonym_name):
            query = f"CREATE (n:OboSynonym {{name: '{synonym.synonym_name}'}})"
            with nju.driver.session() as session:
                session.run(query)
        query = f"MATCH (o:OntologyTerm {{id: '{obt.id}'}}), (s:OboSynonym {{name: '{synonym.synonym_name}'}}) CREATE (o)-[:HAS_SYNONYM {{type: '{synonym.type}'}}]->(s)"
        with nju.driver.session() as session:
            session.run(query)
        # if the OboSynonym has pmids, process the pmids
        for pubmed_id in synonym.pmids:
            create_or_update_pubmed_article_node([pubmed_id])
            # create a relationship between the OboSynonym and PubMedArticle nodes in the database.
            # The relationship between the OboSynonym and PubMedArticle nodes is labeled as CITES
            query = f"MATCH (s:OboSynonym {{name: '{synonym.synonym_name}'}}), (p:PubMedArticle {{pub_id: {pubmed_id}}}) CREATE (s)-[:CITES]->(p)"