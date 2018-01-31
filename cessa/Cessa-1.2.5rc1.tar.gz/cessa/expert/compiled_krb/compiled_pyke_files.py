# compiled_pyke_files.py

from pyke import target_pkg

pyke_version = '1.1.1'
compiler_version = 1
target_pkg_version = 1

try:
    loader = __loader__
except NameError:
    loader = None

def get_target_pkg():
    return target_pkg.target_pkg(__name__, __file__, pyke_version, loader, {
         ('', '', 'questions.kqb'):
           [1496070490.552219, 'questions.qbc'],
         ('', '', 'question_fact.kfb'):
           [1496070490.565078, 'question_fact.fbc'],
         ('', '', 'syscall.kfb'):
           [1496070490.610265, 'syscall.fbc'],
         ('', '', 'argument.kfb'):
           [1496070490.612955, 'argument.fbc'],
         ('', '', 'bc_relate.krb'):
           [1496070490.643758, 'bc_relate_bc.py'],
         ('', '', 'question_rule.krb'):
           [1496070490.64867, 'question_rule_bc.py'],
         ('', '', 'macro.kfb'):
           [1496070490.659138, 'macro.fbc'],
        },
        compiler_version)

