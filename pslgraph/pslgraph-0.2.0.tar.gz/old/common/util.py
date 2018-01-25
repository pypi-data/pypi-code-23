import os
import re
import subprocess

from .constants import *

# Run the PSL model using the CLI and return the output (stdout).
def runPSL(model = 'unified', postgresDBName = DEFAULT_POSTRGES_DB_NAME):
    rulesPath = os.path.join(PSL_CLI_DIR, "%s.psl" % (model))
    dataPath = os.path.join(PSL_CLI_DIR, "%s.data" % (model))

    dbOption = ''
    if (postgresDBName and postgresDatabaseAvailable(postgresDBName)):
        dbOption = "--postgres '%s'" % (postgresDBName)

    pslCommand = "java -jar '%s' --infer --model '%s' --data '%s' %s" % (PSL_CLI_JAR, rulesPath, dataPath, dbOption)
    pslOutput = str(subprocess.check_output(pslCommand, shell = True), 'utf-8')

    return pslOutput

# See if we can get a response for the named database.
def postgresDatabaseAvailable(postgresDBName):
    command = "psql '%s' -c ''" % (postgresDBName)

    try:
        subprocess.check_call(command, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, shell = True)
        print("Postgres successfully discovered.")
    except subprocess.CalledProcessError:
        print("Postgres not found - using H2 instead.")
        return False

    return True

# Returns all the link predicates found in the PSL output.
# Returns: {G1Id: {G2Id: Score, ...}, ...}
def getLinksFromPSL(pslOutput):
    links = {}

    for line in pslOutput.splitlines():
        line = line.strip()

        match = re.match(r"^LINK\('(\d+)::(\w+)', '(\d+)::(\w+)'\) = (\d+\.\d+)", line)
        if (match != None):
            g1Id = match.group(2)
            g2Id = match.group(4)
            score = float(match.group(5))

            if (g1Id not in links):
                links[g1Id] = {}

            if (g2Id not in links[g1Id]):
                links[g1Id][g2Id] = {}

            links[g1Id][g2Id] = score

    return links

def writeTSV(path, rows):
    with open(path, 'w') as file:
        # TODO(eriq): Batch
        for row in rows:
            file.write("\t".join(row) + "\n")

# Look for data in specific columns in a csv.
def readHeaderCSV(path, desiredColumns = None):
    if (desiredColumns is None or len(desiredColumns) == 0):
        raise("Columns not specified")

    data = []

    with open(path, 'r') as csvFile:
        # Pick up the header so we can tell which column we want.
        header = next(csvFile)

        indexes = [-1] * len(desiredColumns)

        columnNames = header.strip().split(',')
        for i in range(len(columnNames)):
            if (columnNames[i] in desiredColumns):
                indexes[desiredColumns.index(columnNames[i])] = i

        for i in range(len(indexes)):
            if (indexes[i] == -1):
                raise("Could not find all desired column: '%s'." % (desiredColumns[i]))

        for line in csvFile:
            parts = [part.strip() for part in line.split(',')]

            row = []
            for index in indexes:
                row.append(parts[index])
            data.append(row)

    return data
