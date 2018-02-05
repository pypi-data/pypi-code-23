"""
XDSM PDF writer utility

Original author:
    A.B.Lambe lambe@utias.utoronto.ca
Modified By:
    David Chen greatcwmine@gmail.com
    Lukas Mueller lukas.mueller94@gmail.com
"""


import tempfile
import os
import shutil
import subprocess
import unicodedata
import threading

from kadmos.utilities.general import format_string_for_latex
from distutils.spawn import find_executable


class XDSM(object):

    def __init__(self, xdsm_path=None):
        self.inds = {}
        self.comps = []
        self.deps = []
        self.chains = []
        self.process = None

        if xdsm_path:
            self._xdsm_path = xdsm_path
        else:
            import os
            self._xdsm_path = os.path.dirname(os.path.abspath(__file__))

    # noinspection PyMethodMayBeStatic
    def _is_empty_comp(self, name):
        """Define empty node rule"""
        if name[:5] == 'EMPTY':
            return True
        else:
            return False

    def addComp(self, name, style, string, stack=False):
        """Add component

        :param name: label of the component, using EMPTY heading keyword to specify EMPTY node (e.g. overall inputs and
        outputs)
        :type name: str
        :param string: name of the component that appears in the pdf
        :type string: str
        :param style: tikz block style, defined in diagram_styles.tex
        :type style: str
        :param stack: adds the stack option
        :type stack: bool
        """
        if name[0:5] != 'EMPTY':
            name = unicodedata.normalize('NFKD', name.decode('unicode-escape')).encode('hex')
        string = format_string_for_latex(string)
        self.inds[name] = len(self.comps)
        self.comps.append([name, style, string, stack])

    def addDep(self, out, inp, style, string, stack=False):
        """Add dependency

        :param out: label of the component that depends on the variable
        :type out: str
        :param inp: label of the component that computes the variable
        :type inp: str
        :param style: tikz block style, defined in diagram_styles.tex
        :type style: str
        :param string: name of the variable that appears in the pdf
        :type string: str
        :param stack: adds the stack option
        :type stack: bool
        """
        if out[0:5] != 'EMPTY':
            out = unicodedata.normalize('NFKD', out.decode('unicode-escape')).encode('hex')
        if inp[0:5] != 'EMPTY':
            inp = unicodedata.normalize('NFKD', inp.decode('unicode-escape')).encode('hex')
        string = format_string_for_latex(string)
        self.deps.append([out, inp, style, string, stack])

    def addChain(self, chain_list):
        """Set the process chain list

        :param chain_list: process chain
        :type chain_list: list
        """
        chain_list_new = []
        for chain_elem in chain_list:
            if chain_elem[0:5] != 'EMPTY':
                chain_list_new.append(unicodedata.normalize('NFKD', chain_elem.decode('unicode-escape')).encode('hex'))
            else:
                chain_list_new.append(chain_elem)
        if len(chain_list_new) < 2:
            raise ValueError('the process chain has 2 elements at least')
        self.chains.append(chain_list_new)

    def _get_cmds(self):
        """Generate the XDSM_writer matrix node"""
        def write(i, j, name, style, string, stack):
            M[i][j] = '    \\node'
            M[i][j] += ' [' + style + (',stack]' if stack else ']')
            M[i][j] += ' (' + name + ')'
            M[i][j] += ' {' + string + '};'
            M[i][j] += ' &\n' if j < n - 1 \
                else (' \\\\\n    %Row ' + str(i+2) + '\n')

        n = len(self.comps)

        inds = self.inds

        names = [[None for j in range(n)]
                 for i in range(n)]

        for name, style, string, stack in self.comps:
            names[inds[name]][inds[name]] = name
        for out, inp, style, string, stack in self.deps:
            names[inds[inp]][inds[out]] = out+'-'+inp

        M = [
            [('    &\n' if j < n - 1 else '    \\\\\n') for j in range(n)]
            for i in range(n)]
        for name, style, string, stack in self.comps:
            # skip EMPTY* component
            if not self._is_empty_comp(name):
                write(inds[name], inds[name], name, style, string, stack)

        for out, inp, style, string, stack in self.deps:
            write(inds[inp], inds[out], out+'-'+inp, style, string, stack)

        H = ['' for i in range(n)]
        for i in range(n):
            minj = i
            maxj = i
            for out, inp, style, string, stack in self.deps:
                j = inds[out]
                if inds[inp] is i and not self._is_empty_comp(inp):
                    minj = j if j < minj else minj
                    maxj = j if j > maxj else maxj
            if minj is not maxj:
                H[i] = '   '
                H[i] += ' (' + names[i][minj] + ')'
                H[i] += ' edge [DataLine]'
                H[i] += ' (' + names[i][maxj] + ')\n'

        V = ['' for jj in range(n)]
        for j in range(n):
            mini = j
            maxi = j
            for out, inp, style, string, stack in self.deps:
                i = inds[inp]
                if inds[out] is j and not self._is_empty_comp(out):
                    mini = i if i < mini else mini
                    maxi = i if i > maxi else maxi
            if mini is not maxi:
                V[j] = '   '
                V[j] += ' (' + names[mini][j] + ')'
                V[j] += ' edge [DataLine]'
                V[j] += ' (' + names[maxi][j] + ')\n'

        return M, H, V

    def _write_construction(self, fun_w):
        """Write the XDSM_writer construction code"""
        n = len(self.comps)
        M, H, V = self._get_cmds()
        w = lambda s: fun_w(s+'\n')
        xpath = self._xdsm_path.replace('\\', r'/')
        w('\\usepackage{geometry}')
        w('\\usepackage{amsfonts}')
        w('\\usepackage{amsmath}')
        w('\\usepackage{amssymb}')
        w('\\usepackage{tikz}')
        w('')
        w('\\input{%s/diagram_border}' % xpath)
        w('')
        w('\\begin{document}')
        w('')
        w('\\input{%s/diagram_styles}' % xpath)
        w('')
        w('\\begin{tikzpicture}')
        w('')
        w('  \\matrix[MatrixSetup]')
        w('  {')
        w('    %Row 1')
        for i in range(n):
            for j in range(n):
                fun_w(M[i][j])
        w('  };')
        w('')
        # for the chain process
        if self.chains:
            w(r'   % XDSM_writer process chains ')
            for i, chn in enumerate(self.chains):
                w(r'   { [start chain=process]')
                w(r'       \begin{pgfonlayer}{process}')
                w(r'       \chainin (%s);' % chn[0])
                last_node = chn[0]
                for e in chn[1:]:
                    if '-' in e or '-' in last_node:
                        w(r'       \chainin (%s)    [join=by ProcessHV];' % e)
                    else:
                        w(r'       \chainin (%s)    [join=by ProcessHV];' % e)

                    last_node = e
                w(r'       \end{pgfonlayer}')
                w(r'   }')
                w('')
        w('  \\begin{pgfonlayer}{data}')
        w('    \\path')
        w('    % Horizontal edges')
        for i in range(n):
            fun_w(H[i])
        w('    % Vertical edges')
        for j in range(n):
            fun_w(V[j])
        w('    ;')
        w('  \\end{pgfonlayer}')
        w('')
        w('\\end{tikzpicture}')
        w('')
        w('\\end{document}')

    def _write(self, filename):
        """Generate latex code"""
        f = open(filename+'.tex', 'w')
        w = lambda s: f.write(s+'\n')
        w('\\documentclass{article}')
        self._write_construction(f.write)
        f.close()

    # noinspection PyMethodMayBeStatic
    def _compilepdf(self, filename, timeout):
        """Use pdflatex to compile the tex file"""
        def target():
            subprocess.check_output('pdflatex ' + filename + '.tex', shell=True, stderr=subprocess.STDOUT,
                                    cwd=os.path.dirname(filename))

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'WARNING: Compiling PDF in create_dsm() function seems to be stuck. Check the compiling tex-file by' \
                  ' setting keep_tex_file=True.'
            thread.join()

    def create(self, file_path, keep_tex_file, compile_pdf):
        """Create a compiled XDSM at the specified file_path"""
        # Create temporary directory
        directory = tempfile.mkdtemp()
        file_name = os.path.join(directory, 'diagram')
        # Proceed if latex is installed
        if find_executable('latex') is not None:
            # Write latex file for compiling
            self._write(file_name)
            # Check if file_path exist and if not create the file_path
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            # Move compiled diagram
            # Remove previous pdf file (if it exists)
            try:
                os.remove(file_path + '.pdf')
            except OSError:
                pass
            # Remove previous tex file (if it exists)
            try:
                os.remove(file_path + '.tex')
            except OSError:
                pass
            # Save tex file
            if keep_tex_file:
                shutil.copy(file_name+'.tex', file_path+'.tex')
            # Compile diagram if desired
            if compile_pdf:
                self._compilepdf(file_name, timeout=10)
                # Try to save pdf file
                try:
                    os.rename(file_name+'.pdf', file_path+'.pdf')
                except OSError:
                    pass
        # In case latex not installed (properly) report error
        else:
            print 'WARNING: Path does not contain latex. Please make sure latex is installed and include it in the path to enable create_dsm() function.'
        # Delete the temporary directory
        shutil.rmtree(directory)
