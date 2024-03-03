from Neo4jFunctions import  neo4j_utils as pmf
import PubMedXMLFunctions as pxf
import JournalArticleNeo4jFunctions as jaf


def get_needs_properties_batch(n):
    """
    Query the database for n nodes that have the needs_properties flag set to true
    Return the result as a String of comma separated integers
    Input: n - the number of nodes to return
    """
    # Define the query
    query = "MATCH (p:`biolink:JournalArticle`) WHERE p.needs_properties = TRUE RETURN p.id AS id limit " + str(n)
    # Return the list of node IDs as a list of integers
    pubmed_ids = [resolve_pmid(pmid) for pmid in pmf.query_node_property_values(query,"id")]
    return pubmed_ids

# Define a function that accepts a string that is composed of a PMID: prefix followed by a number
# and returns the number as an integer

def resolve_pmid(pmid_str):
    """
    Extract the integer value from a string that is composed of a PMID: prefix followed by a number
    """
    return int(pmid_str.split(":")[1])

def main():
    """
    Main function
    Controls the processing of the PubMed data batches
    """
    print("Starting PubMed data import")
    batch_size = 100
    # Loop until all nodes that have the needs_properties flag set to true have been processed
    while pmf.needs_properties_nodes_exist:
        # Get a batch of nodes that have the needs_properties flag set to true
        pubmed_ids = get_needs_properties_batch(batch_size)
        # print(f"Processing batch of {batch_size} nodes: {pubmed_ids}")
        pubmed_articles = pxf.get_pubmed_articles(pubmed_ids)
        if pubmed_articles is None or not pubmed_articles:
            print("No articles returned for pubmed_ids: {pubmed_ids}")
            for pubmed_id in pubmed_ids:
                jaf.negate_needs_props_and_refs(pubmed_id)
        else:
            for pubmed_article in pubmed_articles:
                data = pxf.extract_pubmed_data(pubmed_article)
                # print(f"{data}\n")
                print(f"Processing PMID {data['pmid']}")
                pxf.persist_pubmed_data(data)

    print("Finished PubMed data import")


if __name__ == "__main__":
    main()