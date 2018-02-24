"""This file provides a common class used to collect all of the block options"""

from os import chdir, getcwd


class BlockOptions(object):
    """
    BlockOptions collects all of the options needed to run any of the child
    classes so that its descendants can pull out only what they need.
    """

    USED_KWARGS = [
        'blob',
        'blob_path',
        'blob_working_directory',
        'explicit_lexer_name',
        'external_source_link',
        'git_ref_name',
        'git_ref_hash',
        'git_blob_hash',
        'highlighted_blob',
        'highlighted_blob_styles',
        'inline_css',
        'linenos',
        'no_header',
        'raw',
        'title',
    ]

    blob = None
    blob_path = None
    explicit_lexer_name = None
    external_source_link = None
    git_ref_name = None
    git_ref_hash = None
    git_blob_hash = None
    highlighted_blob = None
    highlighted_blob_styles = None
    inline_css = False
    linenos = True
    no_header = False
    raw = None
    title = None

    working_directory = 'launch_directory'

    def __init__(self, *args, **kwargs):
        """The ctor simply assigns defaults

        Possible parameters:
        blob = None
            The raw file blob to parse
        blob_path = None
            A path to load/parse/etc
        blob_working_directory=os.getcwd()
            The directory to use for input commands
        explicit_lexer_name = None
            Name of lexer to use from Pygments rather than guessing
        external_source_link = None
            Link to the file in VCS
        git_ref_name = None
            Branch/reference name from git
        git_ref_hash = None
            Branch/reference hash from git
        git_blob_hash = None
            Blob hash from git
        highlighted_blob = None
            The highlighted code as an HTML string
        highlighted_blob_styles = None
            The styles to be applied to the highlighted_blob
        inline_css = False
            Inlines all styles
        linenos = True
            Whether or not to generate line numbers
        no_header = False
            Skip header generation on files/named blobs
        raw = None
            Raw input pulled from the first positional argument
        title = None
            The title to use for highlighted blobs or instead of the filename
        """
        if args and args[0]:
            self.raw = args[0]
        self.launch_directory = getcwd()
        self.blob_working_directory = getcwd()
        self.update_options(**kwargs)
        self.move_to_working_directory()
        self.validate()

    def update_options(self, **kwargs):
        """Updates any passed in kwargs; does nothing without values"""
        for option in self.USED_KWARGS:
            if option in kwargs:
                setattr(self, option, kwargs.get(option))

    def move_to_working_directory(self):
        """Moves to the directory of interest"""
        chdir(getattr(self, self.working_directory))

    def validate(self):  # pylint: disable=R0201
        """Overriden by children to validate options"""
        return

    def full_options(self):
        """Compiles a dict with all option values"""
        options = dict()
        for option in self.USED_KWARGS:
            options[option] = getattr(self, option)
        return options

    def return_to_launch_directory(self):
        """Returns to the original directory, where the process was launched"""
        chdir(self.launch_directory)
