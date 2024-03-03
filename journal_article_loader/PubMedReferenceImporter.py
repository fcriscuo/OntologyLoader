# import the neo4j python driver
from neo4j import GraphDatabase
import os

# create a driver object to connect to the database
uri = "neo4j://localhost:7687"
user = os.environ.get('NEO4J_USER', "neo4j")
password = os.environ.get('NEO4J_PASSWORD', "neo4j")
driver = GraphDatabase.driver(uri, auth=(user, password))
print(f"Neo4j Driver created: {driver}")
# define a function to process a reference identifier

def process_reference(pubmed_id, ref_id):
    reference_id = f"PMID:{ref_id}"
    print(f"Processing reference {reference_id} for PubMed article {pubmed_id}")
    # create a session object
    with driver.session() as session:
        # define a cypher query to check if the reference identifier already exists as a PubMedArticle node
        check_query = """
        MATCH (j:`biolink:JournalArticle`)
        WHERE j.id = $reference_id
        RETURN j
        """
        # run the query and get the result object
        result = session.run(check_query, reference_id=reference_id)
        # get the first record from the result object
        record = result.single()
        # check if the record is None
        if record is None:
            # create a new node with the labels PubMedArticle label and the properties pub_id, need_properties, and needs_references
            create_node_query = """
            CREATE (r:`biolink:JournalArticle` {id: $reference_id, need_properties: true, needs_references: false})
            """
            session.run(create_node_query, reference_id=reference_id)
            # print a message that the node was created
            print(f"Reference {reference_id} was created")

        # create a relationship of type CITES between the PubMed node and the Reference node
        create_rel_query = """
        MATCH (p:`biolink:JournalArticle` {id: $pubmed_id})
        MATCH (r:`biolink:JournalArticle` {id: $reference_id})
        MERGE (p)-[:CITES]->(r)
        """
        session.run(create_rel_query, pubmed_id=pubmed_id, reference_id=reference_id)


def persist_reference_data(pubmed_id, reference_ids):
    for reference_id in reference_ids:
        # print(f"PubMedReferenceImporter: processing reference {reference_id} for PubMed article {pubmed_id}")
        process_reference(pubmed_id, reference_id)

# define a main function

def main():
    # get the input values from the user or another source
    pubmed_id = "PMID:24236097"  # example value, change as needed
    reference_ids = [372998,11331753,15851615,15942707,154590,2947748,1689327,1535573,
                     19112498,15192020,16075055,17334357,18697823,19460962,16878133,
                     18025036,17994673,22367739,11193480,11752295,17406303,1826049,
                     11096067,21887363,19096030,17205120,18632605,9590171,3159269,17135268,
                     15944709,17135249,18779589,22541426,18292809,22182733,23575307,9568714,
                     18216245,19717420,20299512,16754881,16940181,18329372,18694565,18694566,17234972,
                     17379774,17468766]

    persist_reference_data(pubmed_id, reference_ids)
    # loop through each reference identifier and process it
    for reference_id in reference_ids:
        process_reference(pubmed_id, reference_id)


# call the main function if the script is run as the main program
if __name__ == "__main__":
    main()

# close the driver object
driver.close()
