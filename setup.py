from setuptools import setup, find_packages

setup(
    name='ontology_loader',
    version='0.1',
    packages=find_packages(),
    description='Python functions to retrieve and load ontologies into Neo4j',
    author='Fred Criscuolo',
    author_email='fcriscuo@genomicsai.dev',
    url='https://github.com/yfcriscuo/OntologyLoader',
    install_requires=[
        'neo4j',
    ],
    classifiers=[
        # Trove classifiers
        # Full list at https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: CCO License',
        'Operating System :: OS Independent',
    ],
)
