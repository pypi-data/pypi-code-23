import pyconrad
import os

def generate_autocomplete_file(file, conrad_dir:str, classname:str, alsoMembers = True):

    if not pyconrad.is_initialized():
        pyconrad.setup_pyconrad(min_ram='50M')

    dir_list = [ conrad_dir ]
    with open(file, 'w') as writer:
        zero_indentation = conrad_dir.count('/') + 1
        writer.writelines('import pyconrad\r\n')
        writer.writelines('import warnings\r\n')
        isroot = True

        while len(dir_list) > 0:
            f = dir_list.pop()
            indentation = f.count('/') - zero_indentation + 1
            if os.path.isdir(f):
                if isroot:
                    isroot = False
                    writer.writelines('class ' + classname + ' (pyconrad.ClassGetter):\r\n')
                    writer.writelines("""
    def __init__(self):
        warnings.warn('This class should never be initialized! Use it as type hint: #type: pyconrad.AutoCompleteConrad')
 
""")
                else:
                    if os.path.basename(f) != 'coneBeam':
                        writer.writelines('    ' * indentation + 'class ' + os.path.basename(f) + ':\r\n')
                for item in os.listdir(f):
                    dir_list.append(os.path.join(f,item))
            if os.path.isfile(f):
                filename, extension = os.path.splitext(os.path.basename(f))
                if extension == '.java' and filename != 'package-info':
                    classname, _ = os.path.splitext(f[len(conrad_dir)+1:])

                    if alsoMembers:
                        try:
                            jclass = pyconrad.JClass(classname.replace('/','.'))
                            writer.writelines('    ' * indentation + 'class ' + filename + ':\r\n')
                            for member in jclass.__dict__:
                                if member != 'class' and member[0] != '_' and member != "and" and member != "lambda":
                                    writer.writelines('    ' * (indentation +1) + member + ' = None\r\n')

                        except:
                            print("fail " + classname.replace('/','.'))
                            writer.writelines('    ' * indentation + filename + ' = None\r\n')
                    else:
                        writer.writelines('    ' * indentation + filename + ' = None\r\n')




if __name__ == '__main__':

    generate_autocomplete_file('/home/stephan/foo.py', '/home/stephan/projects/CONRAD/src', 'AutoCompleteConrad', True)
    print(open('/home/stephan/foo.py','r').read())

import warnings

class AutoCompleteConrad(pyconrad.ClassGetter):
    def __init__(self):
        warnings.warn('This class should never be initialized! Use it as type hint: #type: pyconrad.AutoCompleteConrad')
