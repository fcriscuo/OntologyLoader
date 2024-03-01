"""
A Python script the imports HGNC data into a Neo4j database.
It is intended to update existing `biolink:Gene` nodes with data from the hgnc_complete_set.txt file.
Python code generated with the help of Github Copilot and GeminiAdvanced AI
"""
import csv
import os
import requests
import io
from neo4j import GraphDatabase
from Neo4jFunctions import neo4j_utils as nju
import pubmed_registry as pr

# --- Configuration ---
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = os.environ.get("NEO4J_PASSWORD")  # Fetch from environment variable
#data_file = "/Volumes/SSD870/data/HGNC/sample_hgnc_complete_set.tsv"  # Replace with your file path
hgnc_url = "https://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/tsv/hgnc_complete_set.txt"
# define the HGNC properties that should be ignored
hgnc_properties_to_ignore = [ "symbol", "name","alias_symbol",	"alias_name", "prev_symbol", "prev_name",
                   "date_approved_reserved", "date_symbol_changed", "date_name_changed", "date_modified"]
hgnc_list_properties = ["xref","synonym","pubmed_id","ccds_id","mane_select"]

# --- Node Label ---
node_label = "`biolink:Gene`" #existing node label in the graph

# --- Connect to Neo4j ---
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def update_or_report(tx, hgnc_id, properties):
    result = tx.run("MATCH (g:{} {{id: $hgnc_id}}) SET g += $props RETURN g".format(node_label),
                    hgnc_id=hgnc_id, props=properties)
    record = result.single()
    if record is None:
        print(f"HGNC ID not found in graph: {hgnc_id}")
    else:
        print(f"Updated HGNC ID: {hgnc_id}")
def process_hgnc_row(row, fields):
    hgnc_id = row["hgnc_id"]  # Assuming the ID is always present
    properties = {key: row[key] for key in fields if key != "hgnc_id"}  # Create properties dict
    # Convert delimited list properties to list (eg. xref, synonym, pubmed_id, ccds_id, mane_select)
    properties = nju.convert_selected_properties_to_neo4j_list(properties, hgnc_list_properties)
    #session.execute_write(update_or_report, hgnc_id, properties)
    # process the pubmed_id property if it exists and it is not empty
    # covert the pubmed_id property to a python list
    if "pubmed_id" in properties and properties["pubmed_id"] is not None and properties["pubmed_id"] != "[]":
        pr.register_pubmed_article_nodes(nju.neo4j_array_to_list(properties["pubmed_id"]), hgnc_id)

# --- Data Import Logic ---
with driver.session() as session:
    response = requests.get(hgnc_url, stream=True)
    response.raise_for_status()
    text_stream = io.StringIO(response.text)
    reader = csv.DictReader(text_stream, delimiter='\t')
    headers = reader.fieldnames  # Get field names from the file
    fields =[x for x in headers if x not in hgnc_properties_to_ignore]
    for row in reader:
       process_hgnc_row(row, fields)
    print("All HGNC data imported")
driver.close()
print("Done!")
#