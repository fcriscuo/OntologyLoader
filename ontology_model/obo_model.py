from typing import List
import re
from ontology_model import ontology_registry as ont_reg

# define a function that accepts an ontology id, splits it into prefix and id and resolves the ontology name from the registry
# the split is based on the first colon in the id
def get_ontology_name(id):
    if ':' in id:
        prefix, id = id.split(':', maxsplit=1)
        return ont_reg.get_ontology_name(prefix)
    return ''

# define a funct that removes special characters from the end of a string
def remove_special_characters(input_string):
    return input_string.translate({ord(c): None for c in '[]!,;'})

class Xref:
    def __init__(self, ontology, id,name):
        self.ontology = ontology
        self.term_id = id
        self.name = name

    def generate_xref_from_string(line: str):
        match = re.match(r'xref: (\w+):(\w+) "(.*)"', line)
        if match:
         return Xref(match.group(1), match.group(2), match.group(3))
        else:
            return None

def __str__(self):
    return f"Ontology: {self.ontology}, ID: {self.term_id}, name: {self.name}"

class OboSynonym:
    def __init__(self, input_string):
        self.synonym_name = input_string.split('"')[1]
        self.type = input_string.split(' ')[1]
        self.pmids = [int(remove_special_characters(x[5:])) for x in input_string.split() if x.startswith('PMID:')]

class OboRelationship:
    def __init__(self, type, id, term_name, part_of = False):
        self.type = type
        self.id = id
        self.ontology_name = get_ontology_name(id)
        self.term_name = term_name
        self.part_of = part_of

    def generate_relationship_from_string(line: str):
        parts = line.split(' ')
        type = parts[0].replace(':','')
        part_of = 'part_of' in line
        if part_of:
            id = parts[2]
            term_name = ' '.join(parts[3:]).replace('!', '').lstrip()
        else:
            id = parts[1]
            term_name = ' '.join(parts[2:]).replace('!', '').lstrip()

        return OboRelationship(type, id, term_name, part_of)


    def __str__(self):
        self_str = f"Type: {self.type}, ID: {self.id}, Name: {self.term_name}"

class OboTerm:
    def __init__(self, id: str, term_name: str, namespace: str = '',
                 comment: str = '', definition: str = '',
                 synonyms: List[OboSynonym] = [],
                 relationships: List[OboRelationship] = [],
                 xrefs: List[Xref] = [],
                 pmids: List[int] = []):
        self.id = id
        # if the id contains a ':' then split it into prefix and id and resolve the ontology name from the registry

        self.term_name = term_name
        self.namespace = namespace
        self.comment = comment
        self.definition = definition
        self.synonyms = synonyms
        self.relationships = relationships
        self.xrefs = xrefs
        self.pmids = pmids

    # initialize a placeholder OboTerm object
    # define a function that accepts an ontology id and term name and initializes an OboTerm object
    def generate_placeholder_term(id: str, term_name: str):
        return OboTerm(id, term_name)

    def generate_term_from_xref(xref: Xref):
        return OboTerm(xref.term_id, xref.name)

    def __str__(self):
        return (f"ID: {self.id}, Name: {self.term_name}, Namespace: {self.namespace},"
                f" Comment: {self.comment}, Definition: {self.definition}, Synonyms: {self.synonyms}")
