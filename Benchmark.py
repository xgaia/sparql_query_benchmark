#! /usr/bin/python3

import time
import os
import re
import csv
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

def launch_query(query, endpoint, method):
    """
    launch a query in a endpoint
    :query: a string of the query
    :endpoint: the sparql endpoint
    :method: method: POST or GET
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setCredentials('dba', 'dba')
    sparql.method = method
    sparql.queryType = 'SELECT'
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.query().convert()

def empty_database(endpoint, grph):
    """
    delete all data of an endpoint
    :endpoint: the sparql endpoint
    """
    launch_query('CLEAR GRAPH <'+grph+'>', endpoint, 'POST')

def fill_database(path, endpoint, grph):
    """
    load data into the endpoint
    :path: the datafile (turtle)
    :endpoint: the sparql endpoint
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
            #print(block)
            #print('-------')
            launch_query(prefix_string+' INSERT DATA { GRAPH <'+grph+'> {'+block+'} }', endpoint, 'POST')
            block = ''

            




        #launch_query(prefix_string+' INSERT DATA { GRAPH <'+grph+'> {'+line+'} }', endpoint, 'POST')

    #launch_query(prefix_string+' INSERT DATA { GRAPH <'+grph+'> {'+new_ttl_string+'} }', endpoint, 'POST')


def benchmark(query, endpoint, method):
    """
    benchmark query

    :return: time of query (ms)
    :rtype: float
    """
    start = time.time()
    launch_query(query, endpoint, method)
    end = time.time()
    diff = end - start
    return diff


data_dir = './data/'
gene_dir = data_dir+'gene/'
snp_dir = data_dir+'snp/'

query_dir = './query/'


triple_stores = {
    #'fuseki' : {
    #    'query_endpoint' : 'http://localhost:3030/database/sparql',
    #    'update_endpoint' : 'http://localhost:3030/database/update',
    #    'graph' : 'default'
    #},
    'virtuoso' : {
        'query_endpoint' : 'http://localhost:8890/sparql/',
        'update_endpoint' : 'http://localhost:8890/sparql/',
        'graph' : 'benchmark'
    }
}

for triple_store, endpoints in triple_stores.items():
    print('=======> triplestore : '+triple_store)
    query_endpoint = endpoints['query_endpoint']
    update_endpoint = endpoints['update_endpoint']
    graph = endpoints['graph']

    for gene_file in os.listdir(gene_dir):
        for snp_file in os.listdir(snp_dir):
            #print(gene_file)

            # empty database
            print('--> empty database')
            empty_database(update_endpoint, graph)
            # refill
            print('--> refill with '+gene_file+' and '+snp_file)
            fill_database(gene_dir+gene_file, update_endpoint, graph)
            fill_database(snp_dir+snp_file, update_endpoint, graph)

            #sys.exit(0)
            
            # query
            for query_file in os.listdir(query_dir):
                print('--> query : '+query_file)

                fp = open(query_dir+query_file)
                query_str = fp.read()
                msg = triple_store+'\t'+gene_file+'\t'+query_file
                exec_time = benchmark(query_str, query_endpoint, 'GET')
                print('---> query executed in '+str(exec_time)+' ms')

                # write log file


print('done !')



