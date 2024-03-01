CREATE CONSTRAINT biolink_unique_id FOR (e:`biolink:Entity`) REQUIRE e.id IS UNIQUE
CREATE CONSTRAINT biolink_unique_iri FOR (e:`biolink:Entity`) REQUIRE e.iri IS UNIQUE
// vector index
                                                            // Create a vector index for the abstract property in JournalArticale nodes
CREATE VECTOR INDEX `abstract-embeddings`
FOR (n:`biolink:JournalArticle`) ON (n.embedding)
OPTIONS {indexConfig: {
 `vector.dimensions`: 748,
 `vector.similarity_function`: 'cosine'
}}