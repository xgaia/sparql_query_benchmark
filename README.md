## SPARQL Benchmark

### Dependencies

This script use python3 and the SPARQLWrapper module:

    sudo apt-get install python3 pip3
    pip3 install SPARQLWrapper

### Usage:

#### config file

First, edit the config file with the triplestore informations.

+ query_endpoint: the sparql query endpoint of the triplestore
+ update_endpoint: the sparql update endpoint
+ graph: the rdf graph where data will be stored
+ daemon: name of the daemon of the triplestore, use to restart and stop the triplestore

#### Script

The script take several arguments:

+ `-h`: diplay the help message
+ `-t`, `--triplestore`: the triplestore to test, work with fuseki and virtuoso
+ `-d`, `--data`: a data directory who contain .ttl files. You have to provide 2 directory
+ `-q, `--query`: the query dir who contain the .sparql query files
+ `-o`, `--output-file`: the name of the output file (optional, default: results.csv)
+ `--restart-service`: when the script change triplestore, stop it and start the other.

note: to use the `--restart-service` option, the script execute the `sudo service` command, so you have to provide your root password (or allow this command to be executed without password)
