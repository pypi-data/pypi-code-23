import pysubmit.template as t
import pysubmit.config as c
import os
import stat
import argparse

# ==============================================================================
#                                Sub commands
# ==============================================================================

def generateFunc(args):
    
    # Load CLI parameters
    template                        = args.template
    summarize                       = args.summarize
    
    # Load config
    c                               = args.config
    
    # Check template validity
    template_valid = t.check_template_validity(template, c)
    if not template_valid:
        print()
        print("ERROR: The given 'template' name is not valid. It is needed by operation mode.")
        print("Abort.")
        print()
        exit(1)
    
    # Template object
    temp = t.Template(template, c)

    # Create files
    files = temp.create_files(summarize)
    print()
    print("Done.")
    print()
    print("Created files:")
    for ff in files:
        print("\t{}".format(ff))
    print()

def summarizeFunc(args):
    
    # Short cuts
    files = args.files
    p = args.path
    c = args.config
    n = args.name if args.name is not None else c.get("summarize_output")
    
    # Write text
    lines = []
    ctr = 0
    for file in files:
        full_path = os.path.join(p, file)
        s = "{} {}".format(c.get("submit_command"), full_path)
        ctr += 1
        lines.append(s)
    lines.insert(0, "# Summarized files: {}\n".format(ctr))
    lines.append("\n")
    
    # Create folder
    if not os.path.exists(c.get("output")):
        os.makedirs(c.get("output"))
    
    # Write file
    file_name = os.path.join(c.get("output"), n)
    with open(file_name, "w") as f:
        f.write("\n".join(lines))
        
    # Make it executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)
        
    # Feedback
    print()
    print("Done.")
    print()
    print("Created files:")
    print("\t{}".format(file_name))
    print()
    
    # TODO:
    # * Check files
    
def templatesFunc(args):
    print()
    print("All implemented templates:")
    print()
    template_dir = args.config.get("templates")
    s = "\t {:0"+str(len(str(len(os.listdir(template_dir)))))+"}: {} | {}"
    for i, template in enumerate(os.listdir(template_dir)):
        valid = t.check_template_validity(template, args.config)
        valid_string = u"\u2713" if valid else u"\u2717"        
        print(s.format(i, valid_string, template))
    print()

# ==============================================================================
#                                CLI hook
# ==============================================================================

def parsers():
    """Parsers and logic for CLI hook of PySubmit."""

    # Create the top-level parser
    parser = argparse.ArgumentParser(description="PySubmit computation submission tool.")
    subparsers = parser.add_subparsers()

    # Create the subparser "generate"
    generateParser = subparsers.add_parser("generate",
                                           help="Generate start scripts.")
    generateParser.add_argument("template", help="The template to use.")
    generateParser.add_argument("-sum", "--summarize", action="store_true",
                                help="Summarize the generated start scripts if set.")
    generateParser.set_defaults(func=generateFunc)

    # Create the subparser "summarize"
    summarizeParser = subparsers.add_parser("summarize",
                                            help="Summarize start scripts.")
    summarizeParser.add_argument("files", nargs="+",
                                 help="Files to summarize.")
    summarizeParser.add_argument("-n", "--name", required=False,
                                 help="The summary's name. It becomes 'output/{name}.sh'. Default: In config.")
    summarizeParser.add_argument("-p", "--path", required=True,
                                 help="The start scripts' target path. It becomes '{path}/{files}' in the saved file.")
    summarizeParser.set_defaults(func=summarizeFunc)

    # Create the subparser "templates"
    templatesParser = subparsers.add_parser("templates",
                                            help="Show available templates.")
    templatesParser.set_defaults(func=templatesFunc)

    # Parsing
    args = parser.parse_args()
    
    # Call the working function or show help if called without sub command
    if hasattr(args, "func"):
        # Attach a config object to parsing result
        config_path = os.path.expanduser("~/.pysubmitrc")
        if not os.path.exists(config_path):
            print()
            print("No configuration file found under: '{}'".format(config_path))
            print()
            print("Abort.")
            print()
            print("Find an example under 'examples/pysubmitrc'.")
            print()
            exit()
        config = c.Config(config_path)
        args.config = config
        args.func(args)
    else:
        args = parser.parse_args(["-h"])
