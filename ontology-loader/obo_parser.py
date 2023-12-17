import urllib.request
from typing import List
from ontology_model import obo_model as om

def parse_obo_file(url: str) -> List[om.OboTerm]:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
    terms = []
    for term_str in content.split('\n\n[Term]\n'):
        # if the term_str does not start with 'id' then continue
        if not term_str.startswith('id:'):
            continue
        if 'is_obsolete: true' in term_str or 'OBSOLETE' in term_str:
            continue
        term = om.OboTerm('', '', '', '', '', [],
                       [], [],[])
        for line in term_str.split('\n'):
            if line.startswith('id:'):
                term.id = line[4:]
                if ':' in term.id:
                    term.ontology_name = om.get_ontology_name(term.id)
                else:
                    term.ontology_name = ''
            elif line.startswith('name:'):
                term.name = line[6:]
            elif line.startswith('namespace:'):
                term.namespace = line[11:]
            elif line.startswith('comment:'):
                term.comment = line[9:]
            elif line.startswith('def:'):
                term.definition = line[5:].split('"')[1]
                if 'PMID:' in line:
                    term.pmids = extract_pmids(line[5:].split('"')[2].replace(']',''))
            elif line.startswith('synonym:'):
                term.synonyms.append(om.OboSynonym(line))
            elif line.startswith('is_a:'):
                term.relationships.append(om.OboRelationship.generate_relationship_from_string(line))
            elif line.startswith('intersection_of:'):
                term.relationships.append(om.OboRelationship.generate_relationship_from_string(line))
            elif line.startswith('relationship:'):
                rel = om.OboRelationship.generate_relationship_from_string(line)
                term.relationships.append(rel)
            elif line.startswith('xref:'):
                term.xrefs.append(om.Xref.generate_xref_from_string(line))
        terms.append(term)
    return terms

def extract_pmids(string):
     return [int(item.strip()[5:]) for item in string.split(',') if item.strip().startswith('PMID:')]

if __name__ == "__main__":
    url = "http://purl.obolibrary.org/obo/go.obo"
    terms = parse_obo_file(url)
    print(f"Ontology has {len(terms)} terms.")
    for i in range(1500,3000):
        print(terms[i])
        if len(terms[i].relationships):
            [print(terms[i].relationships[j].__dict__ ) for j in range(len(terms[i].relationships))]
        if len(terms[i].pmids):
            print(terms[i].pmids)
        if len(terms[i].xrefs):
            print("++++ Xrefs")
            [print(terms[i].xrefs[j].__dict__) for j in range(len(terms[i].xrefs))]



