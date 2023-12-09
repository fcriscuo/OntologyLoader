import pronto


def parse_obo(file_path):
    # Load the ontology
    ontology = pronto.Ontology(file_path)
    # ontology = pronto.Ontology.from_obo_library("go.obo")

    # Print out some information about the ontology
    print(f"Ontology has {len(ontology)} terms.")
    #print(ontology.terms["GO:1905176"])
    # Iterate through terms in the ontology and print their names and IDs
    #print(f"Term: {term}")
    # print(f"Term ID: {term.id}, Name: {term.name}")

if __name__ == "__main__":
    # Replace with the path to your go.obo file
    file_path = '/Users/fcriscuo/softwaredev/OntologyLoader/data/go.obo'
    parse_obo(file_path)
