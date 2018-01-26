from dupfileremover import duplicateChecker as dc
import click
import os


@click.command()
@click.argument('folders', nargs=-1)
@click.option('--number',
              '-n',
              default=1,
              type=int,
              help='The maximum number of each file that should be found (default is 1)')
def cli(number, folders):
    """Entry point for dupfileremover.
        :param number: An Int, an option number that tells how many of each identical file is allowed to be found
        :param folders: A String, required argument that gives paths and locations of files that will be used to
        find duplicates
    """
    # if no arguments were passed exit the program
    if len(folders) == 0:
        print("Not enought arguments. Please include a file or folder")
        exit()

    folderList = []
    fileList = []
    print("Combining all files into a master list...")
    try:
        for i in folders:
            if(os.path.isdir(i) is True):
                folderList.append(dc.compileFiles(i))

            elif(os.path.isfile(i) is True):
                fileList.append(os.path.relpath(i))

            else:
                print("\nSorry, but {} is neither a file or a folder".format(i))

    except Exception as e:
        print("Something went wrong while creating the master list")
        print(e)

    try:
        flattened = [val for sublist in folderList for val in sublist]

        allFiles = fileList + flattened

        results = dc.hashFiles(allFiles)

    except Exception as e:
        print("Something went wrong combining the files and folders together")
        print(e)

    print("Hashing the files now")
    try:
        for k, v in results.items():
            if(len(v) > number):
                print("----MD5sum: {}----\n".format(k))
                count = len(v)
                for i in v:
                    if(count > 1):
                        print("{}\n".format(i))
                    else:
                        print("{}\n\n".format(i))
                    count -= 1

    except Exception as e:
        print("Error displaying results")
        print(e)

    print("Done")
