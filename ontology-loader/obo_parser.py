import urllib.request
from typing import List


class OboRelationship:
    def __init__(self, type, id, name):
        self.type = type
        self.id = id
        self.name = name
    def __init__(self,line):
        parts= line.translate({ord('!'):None}).split(' ')
        self.type = parts[0].replace('relationship:','')
        self.id = parts[1]
        self.name = ' '.join(parts[2:]).lstrip()

    def __str__(self):
        self_str = f"Type: {self.type}, ID: {self.id}, Name: {self.name}"
class OboTerm:
    def __init__(self, id: str, name: str, namespace: str, comment: str, definition: str,
                 synonyms: List[str],
                 relationships: List[OboRelationship],
                 xrefs: List[str]):
        self.id = id
        self.name = name
        self.namespace = namespace
        self.comment = comment
        self.definition = definition
        self.synonyms = synonyms
        self.relationships = relationships
        self.xrefs = xrefs

def parse_obo_file(url: str) -> List[OboTerm]:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
    terms = []
    for term_str in content.split('\n\n[Term]\n'):
        if 'is_obsolete: true' in term_str or 'OBSOLETE' in term_str:
            continue
        term = OboTerm('', '', '', '', '', [],
                       [], [])
        for line in term_str.split('\n'):
            if line.startswith('id:'):
                term.id = line[4:]
            elif line.startswith('name:'):
                term.name = line[6:]
            elif line.startswith('namespace:'):
                term.namespace = line[11:]
            elif line.startswith('comment:'):
                term.comment = line[9:]
            elif line.startswith('def:'):
                term.definition = line[5:].split('"')[1]
            elif line.startswith('synonym:'):
                term.synonyms.append(line[9:].split('"')[1])
            elif line.startswith('is_a:'):
                term.relationships.append(OboRelationship(line))
            elif line.startswith('intersection_of:'):
                term.relationships.append(OboRelationship(line))
            elif line.startswith('relationship:'):
                rel = OboRelationship(line.replace('relationship:', ' ').lstrip())
                term.relationships.append(rel)
            elif line.startswith('xref:'):
                term.xrefs.append(line[6:].split('!')[0].strip())
        terms.append(term)
    return terms


if __name__ == "__main__":
    url = "http://purl.obolibrary.org/obo/go.obo"
    terms = parse_obo_file(url)
    print(f"Ontology has {len(terms)} terms.")
    for i in range(1000,1500):
        print(terms[i].__dict__)
        if len(terms[i].relationships):
            for j in range(0,len(terms[i].relationships)):
                print(terms[i].relationships[j].__dict__)