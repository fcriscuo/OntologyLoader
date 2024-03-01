from Neo4jFunctions import neo4j_utils as nju
def test_convert_selected_properties():
    """
    Main function
    """
    data = {
        "name": "John",
        "age": "30",
        "skills": "Python|Java|C++"
    }
    keys = ["skills"]
    properties = nju.convert_selected_properties_to_neo4j_list(data, keys)
    print(properties)
    skills = properties["skills"]
    print(skills)
    print(nju.neo4j_array_to_list(skills))
    return

def test_neo4j_array_to_list():
    """
    Test the neo4j_array_to_list function
    """
    array = '["2591067","12345"]'
    print(nju.neo4j_array_to_list(array))
    return

# test if index exists
def test_index_exists():
    """
    Test the index_exists function
    """
    index = "abstract-embeddings"
    print(nju.index_exists(index))
    return


if __name__ == "__main__":
    test_convert_selected_properties()
    test_neo4j_array_to_list()
    test_index_exists()