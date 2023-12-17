# Define a function that accepts a URL and invokes the ontology parser to create a List of OboTerm objects
# for each OboTerm object in the List of OboTerm objects, create an OntologyTerm node in the database
# if the OntologyTerm node does not exist in the database
import obo_parser as op
import  obo_loader as ol
def load_ontology(url):
    """
    Load an ontology from a URL
    """
    terms = op.parse_obo_file(url)
    for term in terms:
        ol.create_or_update_OntologyTerm_node(term)
        ol.process_OntologyTerm_pmids(term)
        ol.process_OntologyTerm_xrefs(term)
        ol.process_OntologyTerm_relationships(term)
        print(f"Processed OboTerm: {term.id}")
    return

# Define a main function that loads the Gene Ontology and the Human Phenotype Ontology

if __name__ == "__main__":
    """
    Load the Gene Ontology and the Human Phenotype Ontology
    """
    load_ontology("http://purl.obolibrary.org/obo/go.obo")
    print("Gene Ontology terms loaded")
    load_ontology("http://purl.obolibrary.org/obo/hp.obo")
    print("Human Phenotype Ontology terms loaded")