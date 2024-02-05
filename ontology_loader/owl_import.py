import rdflib


def parse_owl(file_path):
    # Load the RDF graph
    g = rdflib.Graph()
    g.parse(file_path, format="application/rdf+xml")

    # Print out some information
    print(f"Graph has {len(g)} statements.")

    # Iterate through triples in the graph and print them
    for subj, pred, obj in g:
        print(f"Subject: {subj}, Predicate: {pred}, Object: {obj}")


if __name__ == "__main__":
    # Replace with the path to your go.owl file
    file_path = '/Volumes/SSD870/Ontologies/GeneOntology/go.owl'
    parse_owl(file_path)
