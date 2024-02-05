"""
Represents a Python component that will process a Gene Ontology file in OBO format to enhance the  biolink:OntologyClass
nodes in an existing Monarch Knowledge Graph (KG) in a local Neo4j database.
The application will parse the Gene Ontology file into a collection of OboTerm objects.
It will match each individual OboTerm object to an existing OntologyClass node in the local Neo4j database.
If the OntologyClass node does not exist in the local Neo4j database, the application will log an error message.
If the OntologyClass node does exist in the local Neo4j database, the application will update the node with the Gene Ontology
namespace. The application will also create placeholder nodes for entities represented as xrefs and PubMed ids in the  OboTerm objects.
The application will create relationships between the OntologyClass nodes and the placeholder nodes.
The PubMed placeholder nodes will be labeled as biolink:Article nodes and a CITES relationship will be
 created between the OntologyClass nodes and the PubMed placeholder nodes.
"""
from  ontology_loader import obo_parser as op
from ontology_loader import obo_loader as ol
from Neo4jFunctions import neo4j_utils as nju

def load_ontology(url):
    """
    Load an ontology from a URL
    """
    terms = op.parse_obo_file(url)
    for term in terms:
        if (verify_OntologyClass_node_exists_by_id(term.id)):
            update_OntologyClass_node_with_properties(term)
            if (term.pmids is not None and len(term.pmids) > 0):
              ol.process_OntologyClass_pmids(term)
            print(f"Processed OboTerm: {term.id}")
    return

# Define a function that will accept an OboTerm object as input, verify that the OntologyClass node exists with the same id
# and update the OntologyClass node with the Gene Ontology namespace from the OboTerm object
# use the neo4j_utils update_node function to update the OntologyClass node with the Gene Ontology namespace
# the namespace argument should be passed as a dictionary with a single key-value pair

def update_OntologyClass_node_with_properties(term):
    """
    Update the OntologyClass node with the Gene Ontology namespace and any xref ids
    """
    if (verify_OntologyClass_node_exists_by_id(term.id)):
        if (term.xrefs is not None or len(term.xrefs) > 0):
            xrefs = ol.format_OntologyClass_xrefs(term)
            nju.update_node(label="`biolink:OntologyClass`", id_prop="id", id_value=term.id,
                            properties={"namespace": term.namespace,"xrefs": ol.format_OntologyClass_xrefs(term)})
        else:
            nju.update_node(label="`biolink:OntologyClass`", id_prop="id", id_value=term.id,
                        properties={"namespace": term.namespace })
    return



# define a function that accepts a String representing a GeneOntology id and verifies that the id
# matches the id property of an existing OntologyClass node in the local Neo4j database

def verify_OntologyClass_node_exists_by_id(id):
    """
    Verify that the OntologyClass node exists in the local Neo4j database
    """
    if (nju.node_exists(label="`biolink:OntologyClass`", id_prop="id", id_value=id)):
        return True
    else:
        print(f"OntologyClass node with id {id} does not exist.")
    return False

