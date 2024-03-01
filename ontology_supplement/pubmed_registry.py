
from Neo4jFunctions import neo4j_utils as nju
def pubmed_article_node_exists(pub_id: int):
    """
    Return True if a node labeled as PubMedArticle exists in the database based on the PubMedArticle's pub_id property
    """
    return nju.node_exists("PubMedArticle", "pub_id", str(pub_id))

# A function that accepts a list of PubMed identifiers as either integers or strings
# and if novel in the underlying Neo4j database creates a new placeholder node labeled as PubMedArticle
# The needs_properties and needs_references properties are set to True, indicating that this node requires additional properties and references
# If the node already exists in the database, the function will update the node's iri property with the PubMed URL as
# well as ensuring that biolink ontology labels are applied to the node.
# Finally, the function will create a CITES relationship between the PubMedArticle node and the specified database node
def register_pubmed_article_nodes(pubmed_articles: list, db_id:str):

    for pubmed_id in pubmed_articles:
        if not pubmed_article_node_exists(pubmed_id):
            query = (f"CREATE (n:PubMedArticle:`biolink:Article`:`biolink:Entity`:`biolink:InformationContentEntity`:"
                     f"`biolink:NamedThing`:`biolink:Pubication`:`biolink:JournalArticle` {{ pub_id: {str(pubmed_id)}, "
                     f" category:['biolink:Article','biolink:Entity','biolink:InformationContentEntity','biolink:NamedThing','biolink:Publication',"
                     f" 'biolink:JournalArticle'],iri:'https://pubmed.ncbi.nlm.nih.gov/{str(pubmed_id)}/',"
                     f" needs_properties: TRUE, needs_references: TRUE}})")
        else:
            query = (f"MATCH (n:PubMedArticle) WHERE n.pub_id = {str(pubmed_id)}  AND n.iri is NULL "
                     f" SET n:`biolink:Publication`:`biolink:Article`:`biolink:Entity`:`biolink:InformationContentEntity`:"
                     f"`biolink:NamedThing`:`biolink:Publication`:`biolink:JournalArticle`,"
                     f" n.iri='https://pubmed.ncbi.nlm.nih.gov/{str(pubmed_id)}/'")
        with nju.driver.session() as session:
            try:
                session.run(query)
            except Exception as e:
                print(f"Error creating/updating node for {str(pubmed_id)}")
                print(query)

        query = f"MATCH (e:`biolink:Entity` {{id: '{db_id}'}}), (p:PubMedArticle {{pub_id: {str(pubmed_id)}}}) CREATE (e)-[:CITES]->(p)"
        with nju.driver.session() as session:
            session.run(query)
            print(f"Created relationship between biolink.Entity {db_id} and PubMedArticle {str(pubmed_id)}")
