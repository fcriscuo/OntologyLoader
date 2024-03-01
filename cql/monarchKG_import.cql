# run the following commands to load the database


cd $NEO4J_HOME
# ensure that the database is stopped
./bin/neo4j-admin database load --from-path=/Volumes/SSD870/Ontologies/MonarchKG/monarch-neo4j --overwrite-destination=true   neo4j
./bin/neo4j-admin database migrate --force-btree-indexes-to-range neo4j
./bin/neo4j console

# define the constraints listed in monarchkg_constraints.cql

# load additional ontology properties by executing monarchKG_app.py

# run the following commands to backup the system and neo4j databases
cd $NEO4J_HOME
./bin/neo4j-admin database dump --expand-commands system --to-path=./backups && neo4j-admin database dump --expand-commands neo4j --to-path=./backups