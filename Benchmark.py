#! /usr/bin/python3
"""
SPARQL Benchmark script written by Xavier Garnier
"""

import time
import os
#import re
#import csv
import sys
import getopt
import configparser
from SPARQLWrapper import SPARQLWrapper, JSON

def usage():
    """
    help function
    """
    print('Usage:')
    print('\t./Benchmark.py -t <triplestore> -d <data dir1> -d <data dir2> -q <query_dir>')
    print('\n<triplestore>: virtuoso and/or fuseki')
    print('<data_dir>: contains data files in ttl format')
    print('<query_dir>: contains query files in sparql format')

def get_args(argv):
    """
    Get the arguments of the script

    :argv: list of arguments
    :return: a dict with the parsed arguments
    :rtype: dict
    """
    data = []
    triplestore = []
    results = {}
    query = ''
    try:
        opts, argvs = getopt.getopt(argv, "ht:d:q:", ["triplestore=", "data=", "query="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if not opts:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(2)
        elif opt in ("-t", "--triplestore"):
            triplestore.append(arg)
        elif opt in ("-d", "--data"):
            data.append(arg)
        elif opt in ("-q", "--query"):
            query = arg

    if not triplestore or not data or not query:
        usage()
        sys.exit(2)

    for ts in triplestore:
        if ts not in ('virtuoso', 'fuseki'):
            print(ts+' is not supported (only fuseki and virtuoso)')
            sys.exit(2)

    if len(data) != 2:
        print('This script work with 2 datasets')
        sys.exit(2)

    results['triplestore'] = triplestore
    results['data'] = data
    results['query'] = query
    return results

def get_config(ini):
    """
    Get the triplestore configurations stored in a INI file
    :ini: path of the INI file
    """
    config = configparser.ConfigParser()
    config.read(ini)
    return config

def launch_query(query, endpoint, method, virtuoso_hack):
    """
    launch a query in a endpoint
    :query: a string of the query
    :endpoint: the sparql endpoint
    :method: method: POST or GET
    :virtuoso_hack: True or false, for virtuoso triplestore
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setCredentials('dba', 'dba')
    sparql.method = method
    if virtuoso_hack:
        sparql.queryType = 'SELECT'
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.query().convert()

def empty_database(endpoint, grph, virtuoso_hack):
    """
    delete all data of an endpoint
    :endpoint: the sparql endpoint
    :graph: the graph to delete
    :virtuoso_hack: True or false, for virtuoso triplestore
    """
    launch_query('CLEAR GRAPH <'+grph+'>', endpoint, 'POST', virtuoso_hack)

def fill_database(path, endpoint, grph, virtuoso_hack):
    """
    load data into the endpoint
    :path: the datafile (turtle)
    :endpoint: the sparql endpoint
    :graph: the graph to delete
    :virtuoso_hack: True or false, for virtuoso triplestore
    """
    ttl = open(path, 'r') 
    ttl_string = ttl.readlines()

    prefix_string = ''
    block = ''
    for line in ttl_string:
        if line.startswith('@'):
            if line.startswith('@base'):
                continue
            prefix_string += line.replace('@prefix', 'PREFIX').replace(' .', '')
            continue

        line = line.replace('\n', '')
        block += line+'\n'
        if line.endswith('.'):
            launch_query(prefix_string+' INSERT DATA { GRAPH <'+grph+'> {'+block+'} }', endpoint, 'POST', virtuoso_hack)
            block = ''

def benchmark(query, endpoint, method, virtuoso_hack):
    """
    benchmark query
    :query: a string of the query
    :endpoint: the sparql endpoint
    :method: method: POST or GET
    :return: time of query (ms)
    :rtype: float
    """
    start = time.time()
    launch_query(query, endpoint, method, virtuoso_hack)
    end = time.time()
    diff = end - start
    return diff

### Begin script ###

conf = get_config('triplestore.config.ini')

args = get_args(sys.argv[1:])

data_dirs = args.get('data')
triplestores = args.get('triplestore')
query_dir = args.get('query')

for triple_store in conf.sections():
    if triple_store not in triplestores:
        continue
    print('=======> triplestore : '+triple_store)
    query_endpoint = conf[triple_store]['query_endpoint']
    update_endpoint = conf[triple_store]['update_endpoint']
    graph = conf[triple_store]['graph']
    hack = False
    if triple_store == 'virtuoso':
        hack = True

    data_dir1 = data_dirs[0]
    data_dir2 = data_dirs[1]

    for data_file1 in os.listdir(data_dir1):
        for data_file2 in os.listdir(data_dir2):

            # empty database
            print('--> empty database')
            empty_database(update_endpoint, graph, hack)
            # refill
            print('--> refill with '+data_file1+' and '+data_file2)
            fill_database(data_dir1+'/'+data_file1, update_endpoint, graph, hack)
            fill_database(data_dir2+'/'+data_file2, update_endpoint, graph, hack)
            
            # query
            for query_file in os.listdir(query_dir):
                print('--> query : '+query_file)

                fp = open(query_dir+'/'+query_file)
                query_str = fp.read()
                exec_time = benchmark(query_str, query_endpoint, 'GET', hack)
                print('---> query executed in '+str(exec_time)+' ms')

                #TODO write log file


print('--> empty database')
empty_database(update_endpoint, graph, hack)
print('done !')



