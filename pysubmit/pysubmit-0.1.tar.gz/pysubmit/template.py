# Import statements
import os
import stat
import jinja2
import importlib
import importlib.util

# =============================================================================
#                                   Classes
# =============================================================================

class Template(object):
    
    def __init__(self, name, config):
        """
        Initialize the Template instance.
        
        Input
        -----
        name : string
            The template's name.
        render_me : function
            Custom function that returns a list [x_1, x_2, ...] with
            x_i = (file name, context) a tuple holding a file name and
            a context. The *.template file will be rendered using the
            context - which is a directory providing keys for the
            *.template file - and saved with the file name.
        TODO: TWEAK render_me documentation
        TODO: Config documentation
        """
        self.name = name                            # Template name
        self.path = os.path.join(config.get("templates"), name) # Template path
        self.config = config                        # Config instance
        self.render_me = self._load_render_me()     # Load the render me function
        
    def __str__(self):
        """
        Custom str representation method.
        
        Output
        ------
        __str__ : str
            The string is "Template: {name} at {location}".
        """
        return "Template: {name} at {location}".format(name=self.name, location=self.path)
        
    def _load_render_me(self):
        """
        Loads the template's render() function. It is an object's private method.
        
        Output
        ------
        render() : function
            The template's render() function. It returns: [(fname, context)_i]_i with
            fname being the start script name and context the start script's context
            variables used in the template's boilerplate file.
        """
        
        # Import the module
        spec = importlib.util.spec_from_file_location("renderModule",
                                                      os.path.join(self.path, "render.py"))
        renderModule = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderModule)
        
        # Access the render() function
        render = renderModule.render

        # Return the render funtion
        return render
        
    def create_files(self, summarize=False):
        """
        TODO
        """
        # Load jinja2 template environment
        path = os.path.dirname(os.path.abspath(os.path.join(self.path, self.name)))
        template_environment = jinja2.Environment(autoescape=False,
                                                  loader=jinja2.FileSystemLoader(path),
                                                  trim_blocks=False)
        
        # Actual template object
        t = template_environment.get_template("boilerplate")
        
        # Outdir
        outdir = os.path.join(self.config.get("output"), self.name)
        
        # Create output dir if non-existent
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        
        # Render the template
        files = []
        for file_name, context in self.render_me():
            
            # Rendered template
            rendered_template = t.render(context)
            
            # Full save path. First part is config's output directory and second part is file name
            full_save_path = os.path.join(outdir, file_name)
            
            # Save the rendered file accordingly
            with open(full_save_path, "w") as f:
                f.write(rendered_template)
                
            # Save full save path
            files.append(os.path.abspath(full_save_path))
            
        # Write summary
        if summarize:
            
            # Build file list
            file_names = [os.path.basename(f) for f in files]
            # Write to file
            summarize_file = os.path.join(outdir, self.config.get("summarize_output"))
            with open(summarize_file, "w") as f:
                for line in file_names:
                    f.writelines(self.config.get("submit_command").format(start_script=line)+"\n")
            # Make it executable
            st = os.stat(summarize_file)
            os.chmod(summarize_file, st.st_mode | stat.S_IEXEC)
            # Add to created files
            files.append(os.path.abspath(summarize_file))
                
        # Return all the saved files
        return files
    
# =============================================================================
#                                   Functions
# =============================================================================

def check_template_validity(template_name, config):
    """
    Check if a template_name is a proper PySubmit template.
    
    Input:
        template_name : str    - The template name that is looked up in the template folder.
        config        : Config - The Config object storing the template folder.
    """
    # Preparation
    full_path = os.path.join(config.get("templates"), template_name)
    # Tests
    is_directory = os.path.exists(full_path)
    if is_directory:
        has_content = "render.py" in os.listdir(full_path) \
                            and "boilerplate" in os.listdir(full_path)
    else:
        has_content = False
    # Evaluation
    result = is_directory and has_content
    # Return
    return result
