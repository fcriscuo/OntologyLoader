// Cypher to add the id property to PubMedArticle nodes
// that have been updated with their properties
    // Match nodes in batches
    MATCH (p:PubMedArticle)
    WHERE p.iri IS NOT NULL
    WITH p LIMIT 1000
    // Update the 'id' property
    SET p.id = "PMID:" + p.pub_id


// Cypher to remove the PubMedArticle label from nodes that have been updated
// with their properties
MATCH (n:PubMedArticle:`biolink:JournalArticle`) where n.iri IS NOT NULL
REMOVE n:PubMedArticle

// Cypher to update placeholder PubMedArticle nodes with additional labels, and properties
MATCH (p:PubMedArticle)
// Add new labels
SET p
  :`biolink:Entity`
  :`biolink:NamedThing`
  :`biolink:InformationContentEntity`
  :`biolink:Publication`
  :`biolink:Article`
  :`biolink:JournalArticle`
// Create the 'id' property
SET p.id = "PMID:" + p.pub_id
// Create the 'category' property
SET p.category = ["`biolink:Entity`",
"`biolink:NamedThing`",
"`biolink:InformationContentEntity`",
"`biolink:Publication`",
"`biolink:Article`",
  "`biolink:JournalArticle`"]
// Create the 'iri' property
SET p.iri = "https://pubmed.ncbi.nlm.nih.gov/" + p.pub_id

// Cypher to remove the pub_id property from JournalArticle nodes
MATCH (j:`biolink:JournalArticle`) WHERE j.pub_id > 0
REMOVE j.pub_id


 // Create a vector index for the abstract property in JournalArticale nodes
CREATE VECTOR INDEX `abstract-embeddings`
FOR (n:`biolink:JournalArticle`) ON (n.embedding)
OPTIONS {indexConfig: {
 `vector.dimensions`: 748,
 `vector.similarity_function`: 'cosine'
}}