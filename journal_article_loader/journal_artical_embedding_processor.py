from Neo4jFunctions import neo4j_utils as nju
from rag_components import gemma_embedding_service as ges

# define a function that will return the abstract property for a specified PubMedArticle node
def get_journal_article_abstract(pubmed_id):
    """
    Return the abstract property for the specified biolink:JournalArticle node
    """
    label = "`biolink:JournalArticle`"
    id_prop = "id"
    id_value = f"PMID:{pubmed_id}"
    abstract = nju.get_node_property(label, id_prop, id_value, "abstract")
    return abstract

def get_journal_article_title(pubmed_id):
    """
    Return the title property for the specified biolink:JournalArticle node
    """
    label = "`biolink:JournalArticle`"
    id_prop = "id"
    id_value = f"PMID:{pubmed_id}"
    title = nju.get_node_property(label, id_prop, id_value, "title")
    return title

def generate_journal_article_embedding(pubmed_id):
    """
    Return the embedding property for the specified biolink:JournalArticle node
    """
    abstract = get_journal_article_abstract(pubmed_id)
    title = get_journal_article_title(pubmed_id)
    return ges.generate_embedding(title,abstract)

# Define a function that will delete the embedding property from all biolink:JournalArticle nodes
# This useful when you want to re-generate the embeddings using a different model
def delete_journal_article_embeddings():
    """
    Delete the embedding property from all biolink:JournalArticle nodes
    """
    label = "`biolink:JournalArticle`"
    prop = "embedding"
    nju.delete_property_from_nodes(label, prop)

if __name__ == "__main__":
    embedding = generate_journal_article_embedding(20734177)