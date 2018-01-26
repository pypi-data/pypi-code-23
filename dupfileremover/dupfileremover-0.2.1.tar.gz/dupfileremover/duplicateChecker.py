import os
import hashlib


def compileFiles(path):
    """Takes in a list of files and returns their relative path"""

    file = []
    for root, dirs, files in os.walk(path):
        for name in files:
            file.append(os.path.join(root, name))
    return file


def hashFiles(fileList):
    """Takes in a list containing paths to files and returns a dictionary within
        the hash of the file for the key, and the a list with the paths of all
        files that matched the hash as a value
    """
    results = {}

    for file in fileList:
        with open(file, "rb") as aFile:
            fileContents = aFile.read()
            hash = hashlib.md5(fileContents).hexdigest()
        if hash in results:
            results[hash].append(file)
        else:
            results[hash] = [file]
    return results


def saveResults(results, maxNumDupsWanted):
    """Takes in a dictionary with a MD5 hash for the key, and a list of file
        paths as the value, also a number that will be used to see how many
        times to write results to the file

        :param results: A dict, A hash for the key, a list for the value
        :param maxNumDupsWanted: An Int, tells how many files paths to write to the file
    """
    print("Saving the hashes...")
    with open("duplicates.txt", "w") as textFile:
        for k, v in results.items():
            if(len(v) > maxNumDupsWanted):
                textFile.write("----MD5sum: {}----\n".format(k))
                count = len(v)
                for i in v:
                    if(count > 1):
                        textFile.write("{}\n".format(i))
                    else:
                        textFile.write("{}\n\n".format(i))
                    count -= 1
    print("Done!")
