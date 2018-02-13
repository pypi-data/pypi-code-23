from pyno.tree_model import html as H, TreeSub, TreeNode

# Create a special element for CDATA insertion
class CDATA(TreeSub):
    def construct(self, content):
        return f"<![CDATA[{content}]]>"


# Create a special element that works for including different asset types. eg. javascript and stylesheets
class Include(TreeSub):
    def construct(self, file_path):
        if file_path.endswith('.js'):
            return H.script(type="text/javascript", src=file_path)
        elif file_path.endswith('.css'):
            return H.link(rel="stylesheet", type="text/css", href=file_path)
        else:
            raise ValueError('Included file ending is not supported in H.Include' + file_path)
        # todo consider adding more as it becomes relevant to usage

class Import(TreeSub):
    def construct(self, file_path):
        if file_path.endswith('.js'):
            return H.script(type="text/javascript", src=file_path)
        elif file_path.endswith('.css'):
            return H.link(rel="stylesheet", type="text/css", href=file_path)
        else:
            raise ValueError('Included file ending is not supported in H.Include' + file_path)
        # todo consider adding more as it becomes relevant to usage