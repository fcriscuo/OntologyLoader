"""
A Python application that augments an existing Monarch Knowledge Graph (KG) with additional data
mined from ontology files (e.g. Gene Ontology), and other sources
(e.g. PubMed).
"""
import gene_ontology_processor as gop
if __name__ == "__main__":
    """
    Process OntologyClass nodes in the existing Monarch Knowledge Graph (KG) with data from ontology files
    """

    gop.load_ontology("https://purl.obolibrary.org/obo/go.obo")
    print("Gene Ontology terms loaded from the OBO Library")

