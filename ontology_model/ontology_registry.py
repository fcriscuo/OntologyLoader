#Register an ontology's prefix and name
#Exanple GO Gene Ontology
registry = dict()
registry['GO'] = 'Gene Ontology'
registry['HP'] = 'Human Phenotype Ontology'
registry['Reactome'] = 'Reactome'
registry['DOID'] = 'Disease Ontology'
registry['MetaCyc'] = 'BioCyc'
registry['MESH'] = 'Medical Subject Headings'
registry['NCIT'] = 'National Cancer Institute Thesaurus'
registry['EC'] = 'IUBMB Enzyme Nomenclature'
registry['CHEBI'] = 'Chemical Entities of Biological Interest'
registry['CL'] = 'Cell Ontology'
registry['PR'] = 'Protein Ontology'
registry['SO'] = 'Sequence Ontology'
registry['UBERON'] = 'Uber Anatomy Ontology'
registry['NCBITaxon'] = 'NCBI Taxonomy'
registry['HGNC'] = 'HUGO Gene Nomenclature Committee'
registry['UniProtKB'] = 'Universal Protein Knowledgebase'
registry['RHEA'] = 'The Annotated Reactions Database'
registry['KEGG'] = 'Kyoto Encyclopedia of Genes and Genomes'
registry['KEGG_PATHWAY'] = 'Kyoto Encyclopedia of Genes and Genomes'
registry['KEGG_REACTION'] = 'KEGG_REACTION'
registry['Wikipedia'] = 'Wikipedia'
registry["UM-BBD_enzymeID"] = 'Univ of Minn Biocatalysis Biodegradation DB'
registry["UM-BBD_reactionID"] = 'Univ of Minn Biocatalysis Biodegradation DB'
registry["UM-BBD_pathwayID"] = 'Univ of Minn Biocatalysis Biodegradation DB'
registry["RESID"] = 'RESID Database of Protein Modifications'
registry["NIF_Subcellular"] = 'NIF Subcellular'
registry["SABIO-RK"] = 'SABIO_RK'

# define a function that accepts an ontology prefix and returns the ontology's name
# if the prefix is not in the registry, return the prefix
def get_ontology_name(prefix):
    if prefix in registry.keys():
        return registry[prefix]
    else:
        print(f"{prefix} is not in the registry")
        return prefix.replace('-', '_')

# define a function that accepts an ontology prefix and name and adds it to the registry
# if the prefix is not already in the registry
def add_ontology(prefix, name):
    if prefix not in registry.keys():
        registry[prefix] = name
        print(f"Added {prefix} to the registry")
    else:
        print(f"{prefix} is already in the registry")
