"""
Represents a utility for remediating PubMed references in the knowledge graph
This remediates loading OntologyClass nodes from the Gene Ontology, creating biolink:JournalArticle placeholder nodes,
but failing to create the CITES relationships between the OntologyClass nodes and the JournalArticle nodes
"""

import ontology_loader as ol
import ontology_parser as op
def remediate_pubmed_references(url):
    """
    Load an ontology from a URL
    """
    terms = op.parse_obo_file(url)
    for term in terms:
        ol.process_OntologyClass_pmids(term)
        print(f"Processed PubMed references for OboTerm: {term.id}")
    return

# Define a main function that remediates PubMeed references for the Gene Ontology

if __name__ == "__main__":
    """
    """
    remediate_pubmed_references("http://purl.obolibrary.org/obo/go.obo")
