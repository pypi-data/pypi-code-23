import os
import re
import shutil
from colored import fg, bg, attr
from bymtesting.sysPathHanlder import *


class setuptestworkplace:

    def __init__(self):
        self.packageName = "bymtesting"
        print("\n")

    def printRed(self, text):
        print('%s %s %s' % (fg(1), text, attr(0)))

    def printGreen(self, text):
        print('%s %s %s' % (fg(22), text, attr(0)))

    def isEqual(self, str1, str2):
        return str1.lower() == str2.lower()

    def checkServiceNameAndRootDirname(self, servicename, rootdir):
        dirname = rootdir.lower()
        scrap = ""
        if "integrasjontest" in dirname:
            scrap = dirname.replace("integrasjontest", "")
        elif "test" in dirname:
            scrap = dirname.replace("test", "")
        return self.isEqual(scrap, servicename)

    def replaceCaseSensitiv(self, inputText, strOld, strNew):
        return inputText.replace(strOld, strNew)

    def replaceCaseIgnore(self, inputText, strOld, strNew):
        source_str = re.compile(strOld, re.IGNORECASE)
        replaced = source_str.sub(strNew, inputText)
        return replaced

    def rootDirectory(self):
        currentDir = os.getcwd()
        # return os.path.join(currentDir, self.packageName)
        return currentDir

    def rootLocationOfPackage(self):
        packageRootPath = os.path.dirname(os.path.realpath(__file__))
        # return os.path.join(packageRootPath, self.packageName)
        return packageRootPath

    def fullPath(self, filename):
        currentDir = self.rootDirectory()
        filepath = os.path.join(currentDir, filename)
        return filepath

    def joinpath(self, dirname, subdirname, filename):
        currentDir = self.rootDirectory()
        filepath = os.path.join(
            currentDir, subdirname + "\\", dirname + "\\", filename)
        print(filepath)
        return filepath

    def CopyPythonPathFile(self):
        filename = "setPYTHONPATH.bat"
        currentDir = self.rootDirectory()
        rootLocationOfPackage = self.rootLocationOfPackage()
        sourcePath = os.path.join(rootLocationOfPackage, filename)
        targetPath = os.path.join(currentDir, filename)
        shutil.copy(sourcePath, targetPath)

    def commonDirs(self):
        dirs = ["Autentisering", "Lib", "Autorisasjon", "Cache",
                "Docker", "Seed", "WebApi", "Tests"]
        return dirs

    def walkDir(self, path):
        dirOptions = self.commonDirs()
        list_of_files = {}
        for dir in os.listdir(path):
            if dir in dirOptions:
                dirpath = os.path.join(path, dir)
                arr = []
                for filename in os.listdir(dirpath):
                    # if filename.endswith(".py"):
                    filepath = os.path.join(dirpath, filename)
                    if "__pycache__" not in filename:
                        arr.append(filepath)
                list_of_files[dir] = arr
        return list_of_files

    def makeDir(self, dir):
        dirpath = self.fullPath(dir)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        return dirpath

    def makeFile(self, file, text):
        with open(file, "a") as fw:
            fw.write(text)

    def writeToFile(self, dir, filename, text):
        dirpath = self.makeDir(dir)
        file = os.path.join(dirpath, filename)
        self.makeFile(file, text)

    def readFile(self, file):
        content = ""
        with open(file, "r") as fr:
            for line in fr.readlines():
                content += line
        return content

    def getInitPy(self):
        currentDir = self.rootDirectory()
        initPy = os.path.join(currentDir, "__init__.py")
        return initPy

    def createInitPy(self):
        initPy = self.getInitPy()
        self.makeFile(initPy, "")

    def recreate(self, currentDir, dic, servicename, portnumber):
        servicenameLower = servicename.lower()
        servicenameTitle = servicename.title()
        rootFolder = currentDir.split("\\")[-1]
        if(len(dic) == 0):
            return None
        self.createInitPy()
        for dir, files in dic.items():
            for fil in files:
                content = self.readFile(fil)
                modifiedfilename = fil.replace(
                    "webapi", servicenameLower)
                modifiedfilename = modifiedfilename.replace(
                    "WebApi", servicenameTitle)
                newfilename = modifiedfilename.split("\\")[-1]
                modifiedcontent = content.replace("webapi", servicenameLower)
                modifiedcontent = modifiedcontent.replace(
                    "WebApi", servicenameTitle)
                modifiedcontent = modifiedcontent.replace(
                    "bymtesting", rootFolder)
                modifiedcontent = modifiedcontent.replace(
                    "portnumber", portnumber)
                #dir = dir + "2"
                if(dir == "WebApi"):
                    dir = servicenameTitle
                self.writeToFile(dir, newfilename, modifiedcontent)

    def copyCommonDirectorySubdirs(self, serviceName, portnumber):
        currentDir = self.rootDirectory()
        rootLocationOfPackage = self.rootLocationOfPackage()
        if self.notExecutingInsidePackage():
            walk = self.walkDir(rootLocationOfPackage)
            self.recreate(currentDir, walk, serviceName, portnumber)
        else:
            print("You can not replcae forlders in the current package...\n")

    def notExecutingInsidePackage(self):
        currentDir = self.rootDirectory()
        return ("bymtesting" not in currentDir and "bympythonframework" not in currentDir)

    def modifyCurrentTestClass(self, fil):
        content = self.readFile(fil)
        content.replace("from DockerTestCacheService", "from ")

    def refactorExsitedTesting(self):
        currentDir = self.rootDirectory()
        commonDirs = self.commonDirs()
        backup = self.makeDir("backup")
        testsDir = os.path.join(currentDir, "tests")
        for f in os.listdir(currentDir):
            if f not in commonDirs and (f.endswith(".py")):
                fil = os.path.join(currentDir, f)
                if f.startswith("Test"):
                    shutil.copy(fil, backup)
                    shutil.move(fil, os.path.join(testsDir, f))
                else:
                    shutil.move(fil, backup)
        self.createInitPy()

    def cleanUp(self):
        currentDir = self.rootDirectory()
        dirs = self.commonDirs()
        if "bymtesting" not in currentDir:
            initPy = self.getInitPy()
            if(os.path.exists(initPy)):
                os.remove(initPy)
            for d in dirs:
                dirpath = os.path.join(currentDir, d)
                if os.path.exists(dirpath):
                    shutil.rmtree(dirpath)
            sysPathHandler().RemoveCurrentTestingFromSysPath()

        else:
            print("You can not remove folders from the current package...\n")

    def run(self):
        yesAnswer = ['y', "yes", "Y", ""]
        initial = input(
            "You are about to setup your integrationtestings environemnt. will you continue?(Y/N):")
        initial = initial.strip().lower()
        if initial not in yesAnswer:
            print("\n You have stopped the setup. Try to run the command again if you want to setup testenvironment.\n")
            exit(0)
        else:
            print("\n")

        serviceName = input("Service/project name:")
        serviceName = serviceName.strip()
        if serviceName == "":
            print("Servicename is required.\n")
            exit(0)

        portnumber = input("Service/project portnumber:")
        portnumber = portnumber.strip()
        if portnumber == "" or portnumber.isdigit() == False:
            print("Service portnumber is required.\n")
            exit(0)

        self.CopyPythonPathFile()
        sysPathHandler().AddCurrentTestingToSysPath()
        self.copyCommonDirectorySubdirs(serviceName, portnumber)
        print("Your integrationtest environment now is ready :-)\n")


def refactor():
    obj = setuptestworkplace()
    obj.refactorExsitedTesting()


def clean():
    obj = setuptestworkplace()
    obj.cleanUp()


def main():
    obj = setuptestworkplace()
    obj.run()


if __name__ == "__main__":
    main()
