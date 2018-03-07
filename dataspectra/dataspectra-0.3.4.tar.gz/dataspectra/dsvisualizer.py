#!/usr/bin/env python2.7

from __future__ import print_function

'''
dsvisualizer.py [input param file]  [projectid

The output will be in the same directory.  as the parameter file. 
It will be called. dataspectra_output
'''
import argparse, sys, os, shutil
from site_generator import SiteGenerator

packageDirPath = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

def run():
    parser = argparse.ArgumentParser(description = "Data Spectra")
    parser.add_argument("mode", choices=["test", "get", "run", "develop",
         "developclean", "fulldeploy", "developsave", "upload", "push", "storage", "deploy"], help="Specifies the method to run")
    parser.add_argument("-i", "--input", help="Path for main parameter file")
    parser.add_argument("-o", "--output", help="Path for dataspectra output")
    parser.add_argument("-t", "--tutorial", help="Directory where the brainspan files are downloaded to")
    parser.add_argument("-cmd", default="none", choices=["none", "upload", "push", "storage"])
    parser.add_argument("-p", "--projectid", help="projectID from your setup")
    parser.add_argument("-c", "--credentials", help="Path to credential file")
    args = parser.parse_args()

    if args.mode=="test":
        print("Running Tests")

    if args.mode=="fulldeploy":
        print("Deploying your app to google cloud server.")
        print("Running both the deploy and upload.")

        if args.input==None or args.projectid==None:
            sys.exit("Error: Need to specify the input and projectid. Exiting. ") 
        if args.credentials==None:
            sys.exit("Error: Need to specify a path to the credential file with -c")
        if args.output==None:
            args.output = os.path.join(
                os.path.dirname(
                    os.path.realpath(args.input)), 
                    "dataspectra_output"
                    )
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.credentials.rstrip()
        siteClass = SiteGenerator(args.input, args.output, packageDirPath, args.projectid)
        siteClass.production_push_website(args.projectid)
        siteClass.production_upload_datastore(args.projectid)
        siteClass.cloudstorage_upload_datasets(args.projectid)


    if args.mode=="get":
        print("Copying files to current directory.")
        src = os.path.join(packageDirPath, "ds_files")
        dest = os.path.join(cwd, "ds_files")
        shutil.copytree(src, dest)
        print("...Copying complete")

    if args.mode=="develop":
        print("For rapid development purposes")
        if args.input==None:
            args.input = os.path.join(
                packageDirPath, 
                "ds_files", 
                "tutorial_files", 
                "ds.tutorial.parameters.xlsx"
                )
        if args.output==None:
            args.output = os.path.join(cwd, "dataspectra_development_output")
        siteClass = SiteGenerator(args.input, args.output, packageDirPath, args.projectid)
        print("\t Using input: ", args.input)

    if args.mode=="developsave":
        print("Saving development into package source")
        if args.output==None:
            args.output = os.path.join(cwd, "dataspectra_development_output")

        #Copy the static directory file to the aefiles source location. 
        #staticOutput = os.path.join(args.output, "static")
        #staticAefiles = os.path.join(packageDirPath, "aefiles", "static")
        #if os.path.exists(staticAefiles):
        #    print("\tOverwriting current source static directory")
        #    shutil.rmtree(staticAefiles)
        #print("\tCopying output static directory to source static directory")
        #shutil.copytree(staticOutput, staticAefiles)

        #Copy the javascript file to the aefiles source location
        print("\tCopying the javascript to the source static directory")
        jsOutput = os.path.join(args.output, "web", "js")
        jsSource =  os.path.join(packageDirPath, "aefiles", "web", "js")
        if os.path.exists(jsSource):
            print("\tOverwriting current source js directory")
            shutil.rmtree(jsSource)
        shutil.copytree(jsOutput, jsSource)
        #newSearchAuto =os.path.join(args.output, "web", "js", "gene_name_auto.js")
        #aeSearchAuto = os.path.join(packageDirPath, "aefiles", "web", "js", "gene_name_auto.js")
        #shutil.copy2(newSearchAuto, aeSearchAuto)

        #Copy the images to aefiles source location
        #print("\tCopying the images to the source image directory")
        #imageOutput = os.path.join(args.output, "web", "images")
        #imageAefiles = os.path.join(packageDirPath, "aefiles", "web", "images")
        #if os.path.exists(imageAefiles):
        #    print("\tOverwriting current source image directory")
        #    shutil.rmtree(imageAefiles)
        #print("\tCopying output image directory to source image directory")
        #shutil.copytree(imageOutput, imageAefiles)     

        #Copy the tutorial input file to the AE directory
        #print("\tCopying the tutorial input file to the package location. ")
        #packageTutorialFilePath = os.path.join(packageDirPath, "ds_files","tutorial.part1.parameter.xlsx")
        #shutil.copy2(args.input, packageTutorialFilePath)

    if args.mode=="developclean":
        print("For cleaning up after development")
        staticAefiles = os.path.join(packageDirPath, "aefiles", "static")
        aeSearchAuto = os.path.join(packageDirPath, "aefiles", "web", "js", "gene_name_auto.js")
        imageAefiles = os.path.join(packageDirPath, "aefiles", "web", "images")

        #Remove the static directory, 
        if os.path.exists(staticAefiles):
            print("\tCleaning source static directory")
            shutil.rmtree(staticAefiles)
            os.mkdir(staticAefiles)
        
        #Remove the autofill javascript
        if os.path.exists(aeSearchAuto):
            print("\tCleaning autofill javascript")
            os.remove(aeSearchAuto)

        #Remove the images files. 
        if os.path.exists(imageAefiles):
            print("\tCleaning source static directory")
            shutil.rmtree(imageAefiles)
            os.mkdir(imageAefiles)

    if args.mode=="run":
        if args.input==None: 
            sys.exit("Error: Need to specify input. Exiting. ")
        if args.output==None:
            args.output = os.path.join(
                os.path.dirname(
                    os.path.realpath(args.input)), 
                    "dataspectra_output"
                    )
        print("Creating dataspectra files")
        print("\tparameter input file:", args.input)
        print("\tinput directory:", os.path.dirname(os.path.realpath(args.input)))
        print("\tparameter output:", args.output)
        siteClass = SiteGenerator(args.input, args.output, packageDirPath, args.projectid)
    
    if args.mode=="upload":
        if args.output==None:
            args.output = os.path.join(
                os.path.dirname(
                    os.path.realpath(args.input)), 
                    "dataspectra_output"
                    )
        if args.input==None or args.projectid==None:
            sys.exit("Error: Need to specify the input, and projectid. Exiting. ") 
        print("Uploading datasets")
        siteClass = SiteGenerator(args.input, args.output, packageDirPath, args.projectid)
        siteClass.production_upload_datastore(args.projectid)
        siteClass.cloudstorage_upload_datasets(args.projectid)

    if args.mode=="deploy":
        if args.output==None:
            args.output = os.path.join(
                os.path.dirname(
                    os.path.realpath(args.input)), 
                    "dataspectra_output"
                    )
        if args.input==None or args.projectid==None:
            sys.exit("Error: Need to specify the input and projectid. Exiting. ") 
        print("Deploying dataspectra site")
        siteClass = SiteGenerator(args.input, args.output, packageDirPath, args.projectid)
        siteClass.production_push_website(args.projectid)

    if args.mode=="tutorial":
        print("Formatting file for tutorial")
        if args.tutorial==None:
            sys.exit("Error")

    if args.mode =="storage": 
        print("storing")
        if args.output==None:
            args.output = os.path.join(
                os.path.dirname(
                    os.path.realpath(args.input)), 
                    "dataspectra_output"
                    )
        siteClass = SiteGenerator(args.input, args.output, packageDirPath, args.projectid)
        siteClass.cloudstorage_upload_datasets(args.projectid)
