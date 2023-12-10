from Neo4jFunctions import neo4j_utils as nju

# define a function that takes an OboTerm object and determines if a node labeled as OboTerm exists in the database based on the OboTerm's id property

def oboterm_node_exists(obt):
    """
    Return True if a node labeled as OboTerm exists in the database based on the OboTerm's id property
    """
    return nju.node_exists("OboTerm", "id", obt.id)


# define a function that takes an OboTerm object, and based on the OboTerm's id queries if an OboTerm node exists in the database, if not it creates an OboTerm node in the database

def create_or_update_oboterm_node(obt):
    """
    Create or update an OboTerm node in the database
    """
    if not oboterm_node_exists(obt):
        query = f"CREATE (n:OboTerm {{id: '{obt.id}', name: '{obt.name}', namespace: '{obt.namespace}', def: '{obt.def_}'}})"
        with nju.driver.session() as session:
            session.run(query)
    else:
        query = f"MATCH (n:OboTerm {{id: '{obt.id}'}}) SET n.name = '{obt.name}', n.namespace = '{obt.namespace}', n.def = '{obt.def_}'"
        with nju.driver.session() as session:
            session.run(query)
    # If the OboTerm has synonyms, create or update the OboTerm node with an Array of synonyms
    if obt.synonyms:
        query = f"MATCH (n:OboTerm {{id: '{obt.id}'}}) SET n.synonyms = {obt.synonyms}"
        with nju.driver.session() as session:
            session.run(query)
    # If the OboTerm has pmids, process the pmids
    if obt.pmids:
        process_oboterm_pmids(obt)
    # if the OboTerm's id value starts with GO, add a label of GeneOntology to the OboTerm node
    if obt.id.startswith("GO"):
        query = f"MATCH (n:OboTerm {{id: '{obt.id}'}}) SET n:GeneOntology"
        with nju.driver.session() as session:
            session.run(query)

    # define a function that takes an PubMedArticle object and determines if a node labeled as PubMedArticle exists in the database based on the PubMedArticle's pub_id property

def pubmed_article_node_exists(pma):
    """
    Return True if a node labeled as PubMedArticle exists in the database based on the PubMedArticle's pub_id property
    """
    return nju.node_exists("PubMedArticle", "pub_id", pma.pub_id)

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
            query = f"CREATE (n:PubMedArticle {{pub_id: {pubmed_id}, needs_properties: TRUE, needs_references: TRUE}})"
            with nju.driver.session() as session:
                session.run(query)
        else:
            continue

# define a function that takes an OboTerm object and a PubMedArticle object as arguments and creates a relationship between the OboTerm and PubMedArticle nodes in the database

def create_oboterm_pubmed_article_relationship(obt, pma):
    """
    Create a relationship between the OboTerm and PubMedArticle nodes in the database
    """
    query = f"MATCH (o:OboTerm {{id: '{obt.id}'}}), (p:PubMedArticle {{pub_id: {pma.pub_id}}}) CREATE (o)-[:CITES]->(p)"
    with nju.driver.session() as session:
        session.run(query)

# define a function that takes an OboTerm object and processes its List of  pmids
# for each pubmed_id in the List of pmids, create a PubMedArticle node in the database if it does not exist
# and create a relationship between the OboTerm and PubMedArticle nodes in the database

def process_oboterm_pmids(obt):
    """
    Create PubMedArticle nodes and relationships between the OboTerm and PubMedArticle nodes in the database
    """
    for pubmed_id in obt.pmids:
        create_or_update_pubmed_article_node([pubmed_id])
        create_oboterm_pubmed_article_relationship(obt, pubmed_id)

