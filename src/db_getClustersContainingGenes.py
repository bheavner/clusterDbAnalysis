#!/usr/bin/python

# This is a pipe command
# Pipe in a tab-delimited file containing gene IDs
#
# Returns all (run ID, clusterID) pairs containing those gene IDs to stdout
#
# Option -g: Column containing gene ID (default = 1), starting from 1 in the first column
#

import sqlite3, fileinput, optparse
from FileLocator import *

usage = "%prog [options] < gene_ids > clusters_containing_genes"
description = "Given a list of gene IDs, gets a list of clusters containing those genes (in all run IDs)"
parser = optparse.OptionParser(usage=usage, description=description)
parser.add_option("-g", "--gcolumn", help="Column number (start from 1) for gene ID", action="store", type="int", dest="genecolumn", default=1)
(options, args) = parser.parse_args()
gc = options.genecolumn - 1 # Convert to Pythonic indexes                                                                                                                                                      
con = sqlite3.connect(locateDatabase())
cur = con.cursor()

desiredGenes = []
for line in fileinput.input("-"):
    spl = line.strip('\r\n').split("\t")
    # If the file does not include fig|, go ahead and add it automatically.
    if spl[gc].startswith("fig|"):
        desiredGenes.append(spl[gc])
    else:
        desiredGenes.append("fig|%s" %(spl[gc]))

cur.execute("CREATE TEMPORARY TABLE s ( geneid VARCHAR(256) );")

for gene in desiredGenes:
    cur.execute("INSERT INTO s VALUES (?);", (gene, ))

cur.execute("""SELECT clusters.* FROM clusters
               WHERE clusters.geneid IN (SELECT geneid FROM s)
               ORDER BY runid, clusterid; """)

for l in cur:
    s = list(l)
    stri = "\t".join(str(t) for t in s)
    print stri

con.close()
