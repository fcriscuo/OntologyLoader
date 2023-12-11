from typing import List
import re
import ontology_registry as ont_reg

# define a function that accepts an ontology id, splits it into prefix and id and resolves the ontology name from the registry
# the split is based on the first colon in the id
def get_ontology_name(id):
    prefix, id = id.split(':', maxsplit=1)
    return ont_reg.get_ontology_name(prefix)

class Xref:
    def __init__(self, ontology, id,name):
        self.ontology = ontology
        self.term_id = id
        self.name = name

    def __init__(self, line):
        match = re.match(r'xref: (\w+):(\w+) "(.*)"', line)
        if match:
            self.ontology = match.group(1)
            self.term_id = match.group(2)
            self.name = match.group(3)
    def __str__(self):
        return f"Ontology: {self.ontology}, ID: {self.term_id}, name: {self.name}"

class OboSynonym:
    def __init__(self, input_string):
        self.synonym_name = input_string.split('"')[1]
        self.type = input_string.split(' ')[1]
        self.pmids = [int(x[5:]) for x in input_string.split() if x.startswith('PMID:')]

class OboRelationship:
    def __init__(self, type, id, term_name):
        self.type = type
        self.id = id
        self.ontology_name = get_ontology_name(id)
        self.term_name = term_name
    def __init__(self,line):
        parts= line.translate({ord('!'):None}).split(' ')
        self.type = parts[0].replace('relationship:','')
        self.id = parts[1]
        self.ontology_name = get_ontology_name(self.id)
        self.term_name = ' '.join(parts[2:]).lstrip()

    def __str__(self):
        self_str = f"Type: {self.type}, ID: {self.id}, Name: {self.name}"
class OboTerm:
    def __init__(self, id: str, term_name: str, namespace: str = '',
                 comment: str = '', definition: str = '',
                 synonyms: List[OboSynonym] = [],
                 relationships: List[OboRelationship] = [],
                 xrefs: List[Xref] = [],
                 pmids: List[int] = []):
        self.id = id
        self.ontology_name = get_ontology_name(id)
        self.term_name = term_name
        self.namespace = namespace
        self.comment = comment
        self.definition = definition
        self.synonyms = synonyms
        self.relationships = relationships
        self.xrefs = xrefs
        self.pmids = pmids

    # intialize a placeholder OboTerm object
    def __init__(self, id, term_name = ''  ):
        self.id = id
        self.ontology_name = get_ontology_name(id)
        self.term_name = term_name

    # define an __init__ method that accepts an Xref object and initializes an OboTerm object
    def __init__(self, xref: Xref):
        self.id = xref.term_id
        self.ontology_name = get_ontology_name(self.id)
        self.term_name = xref.name

    def __str__(self):
        return (f"ID: {self.id}, Name: {self.term_name}, Namespace: {self.namespace},"
                f" Comment: {self.comment}, Definition: {self.definition}, Synonyms: {self.synonyms}")
