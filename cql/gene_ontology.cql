match (n) detach delete n;
CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE
call n10s.graphconfig.init({ handleVocabUris: "IGNORE"})
call n10s.onto.import.fetch("http://purl.obolibrary.org/obo/go.owl","RDF/XML")
match (n) return count(n);

# create some random Gene nodes
CREATE (:Gene:GO_0035833 {gene_symbol:"ACL", identifier:"A9078"})

# Find genes that are annotated with a specific GO term
CALL n10s.inference.nodesLabelled("GO_0046483",{catNameProp: "name", catLabel: "Class", subCatRel: "SCO"}) yield node return node