# Imports
import logging

from ..utilities.general import get_list_entries


# Settings for the logger
logger = logging.getLogger(__name__)


class KeChainMixin(object):

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def check_kechain(self):
        """Function to check the FPG for validity and completeness in KE-Chain and return the log statements.

        :type self: FundamentalProblemGraph
        :return: result of the check
        :rtype: bool
        """
        # Set check
        nodes_check = True
        formulation_check = True

        # Get variable and function nodes
        n_nodes = self.number_of_nodes()
        func_nodes = self.find_all_nodes(category='function')
        n_functions = len(func_nodes)
        n_variables = len(self.find_all_nodes(category='variable'))
        n_edges = self.number_of_edges()
        prob_var_nodes = self.find_all_nodes(category='variable', subcategory='all problematic variables')
        prob_fun_nodes = self.find_all_nodes(category='function', subcategory='all problematic functions')
        out_nodes = self.find_all_nodes(subcategory='all outputs')

        from time import gmtime, strftime
        logtime = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        log_statements = []
        log_statements.append(['Log start ' + logtime, 'FPG CHECK'])
        log_statements.append(['Log start ' + logtime, 'number of nodes: ' + str(n_nodes)])
        log_statements.append(['Log start ' + logtime, 'number of functions: ' + str(n_functions)])
        log_statements.append(['Log start ' + logtime, 'number of variables: ' + str(n_variables)])
        log_statements.append(['Log start ' + logtime, 'number of edges: ' + str(n_edges)])

        # Check nodes
        # Category A warnings
        log_statements.append(['Nodes check', '-'])
        if n_nodes != (n_functions+n_variables):
            log_statements.append(['WARNING A01', 'Number of total nodes does not match number of function and variable nodes.'])
            nodes_check = False
        if prob_var_nodes:
            log_statements.append(['WARNING A02', 'There are still problematic variable nodes in the graph, namely: ' + \
                  str(prob_var_nodes)])
            nodes_check = False
        if prob_fun_nodes:
            log_statements.append(['WARNING A03', 'There are still problematic function nodes in the graph, namely: ' + \
                  str(prob_fun_nodes)])
            nodes_check = False
        for out_node in out_nodes:
            if 'problem_role' not in self.node[out_node]:
                log_statements.append(['WARNING A04', 'Attribute problem_role is missing on output node:'])
                log_statements.append(['WARNING A04', str(out_node)])
                nodes_check = False
        for func_node in func_nodes:
            if 'problem_role' not in self.node[func_node]:
                log_statements.append(['WARNING A05', 'Attribute problem_role is missing on function node:'])
                log_statements.append(['WARNING A05', str(func_node)])
                nodes_check = False

        if nodes_check:
            log_statements.append(['Nodes check', 'done!'])
        else:
            log_statements.append(['Nodes check', 'done with warnings!'])
            return (nodes_check, log_statements)

        # Check problem formulation
        # Category B warnings
        log_statements.append(['Problem formulation check...', '-'])
        if 'problem_formulation' not in self.graph:
            log_statements.append(['WARNING B01', 'Problem formulation attribute is missing on the graph.'])
            formulation_check = False
        else:
            if 'mdao_architecture' not in self.graph['problem_formulation']:
                log_statements.append(['WARNING B02', 'mdao_architecture attribute is missing in the problem formulation.'])
                formulation_check = False
            else:
                if self.graph['problem_formulation']['mdao_architecture'] not in self.OPTIONS_ARCHITECTURES:
                    log_statements.append(['WARNING B03', 'Invalid mdao_architecture in the problem formulation.'])
                    formulation_check = False
            if 'convergence_type' not in self.graph['problem_formulation']:
                log_statements.append(['WARNING B04', 'convergence_type attribute is missing in the problem formulation.'])
                formulation_check = False
            else:
                if self.graph['problem_formulation']['convergence_type'] not in self.OPTIONS_CONVERGERS:
                    log_statements.append(['WARNING B05', 'Invalid convergence_type %s in the problem formulation.' % \
                          self.graph['problem_formulation']['convergence_type']])
                    formulation_check = False
            if 'function_order' not in self.graph['problem_formulation']:
                log_statements.append(['WARNING B06', 'function_order attribute is missing in the problem formulation.'])
                formulation_check = False
            else:
                func_order = self.graph['problem_formulation']['function_order']
                if len(func_order) != len(func_nodes):
                    log_statements.append(['WARNING B07', 'There is a mismatch between the FPG functions and the given function_order.'])
                    log_statements.append(['WARNING B07', 'namely: %s.' % set(func_nodes).symmetric_difference(set(func_order))])
                    formulation_check = False
            if 'function_ordering' not in self.graph['problem_formulation']:
                log_statements.append(['WARNING B08', 'function_ordering attribute is missing in the problem formulation.'])
                formulation_check = False
            if 'allow_unconverged_couplings' in self.graph['problem_formulation']:
                allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']
                if not isinstance(allow_unconverged_couplings, bool):
                    log_statements.append(['WARNING B09', 'The setting allow_unconverged_couplings should be a Boolean.'])
                    formulation_check = False
            else:
                allow_unconverged_couplings = False
            if self.graph['problem_formulation']['mdao_architecture'] in get_list_entries(self.OPTIONS_ARCHITECTURES, 5, 6): # DOE archs
                if 'doe_settings' not in self.graph['problem_formulation']:
                    log_statements.append(['WARNING B10', 'doe_settings attribute is missing in the problem formulation.'])
                    formulation_check = False
                else:
                    if 'doe_method' not in self.graph['problem_formulation']['doe_settings']:
                        log_statements.append(['WARNING B11', 'doe_method attribute is missing in the doe_settings.'])
                        formulation_check = False
                    elif self.graph['problem_formulation']['doe_settings']['doe_method'] not in self.OPTIONS_DOE_METHODS:
                        doe_method = self.graph['problem_formulation']['doe_settings']['doe_method']
                        log_statements.append(['WARNING B12', 'Invalid doe_method (%s) specified in the doe_settings.' % doe_method])
                        formulation_check = False
                    doe_method = self.graph['problem_formulation']['doe_settings']['doe_method']
                    if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 0, 1, 2):  # FF, LHC, Monte Carlo
                        if 'doe_runs' not in self.graph['problem_formulation']['doe_settings']:
                            log_statements.append(['WARNING B13', 'doe_runs attribute is missing in the doe_settings.'])
                            formulation_check = False
                        elif not isinstance(self.graph['problem_formulation']['doe_settings']['doe_runs'], int) or \
                                        self.graph['problem_formulation']['doe_settings']['doe_runs'] < 0:
                            doe_runs = self.graph['problem_formulation']['doe_settings']['doe_runs']
                            log_statements.append(['WARNING B14', 'Invalid doe_runs (%s) specified in the doe_settings.' % doe_runs])
                            formulation_check = False
                    if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 1, 2): # LHC, Monte Carlo
                        if 'doe_seed' not in self.graph['problem_formulation']['doe_settings']:
                            log_statements.append(['WARNING B15', 'doe_seed attribute is missing in the doe_settings.'])
                            formulation_check = False
                        elif not isinstance(self.graph['problem_formulation']['doe_settings']['doe_seed'], int) or \
                                        self.graph['problem_formulation']['doe_settings']['doe_seed'] < 0:
                            doe_seed = self.graph['problem_formulation']['doe_settings']['doe_seed']
                            log_statements.append(['WARNING B16', 'Invalid doe_seed (%s) specified in the doe_settings.' % doe_seed])
                            formulation_check = False

        if not formulation_check:
            log_statements.append(['Problem formulation check', 'done with warnings!'])
            return (formulation_check, log_statements)

        # If the formulation_check is still True, then check whether the formulation makes sense.
        # Category C warnings
        if formulation_check:
            mdao_arch = self.graph['problem_formulation']['mdao_architecture']
            conv_type = self.graph['problem_formulation']['convergence_type']
            # Check if architecture and convergence_type match
            # match for converged-MDA, MDF, converged-DOE
            if mdao_arch in [self.OPTIONS_ARCHITECTURES[1], self.OPTIONS_ARCHITECTURES[3],
                             self.OPTIONS_ARCHITECTURES[6]]:
                if conv_type not in self.OPTIONS_CONVERGERS[:2]:
                    log_statements.append(['WARNING C01', 'Convergence type %s does not match with architecture %s.' % \
                          (conv_type, mdao_arch)])
                    formulation_check = False
            # match IDF
            if mdao_arch in [self.OPTIONS_ARCHITECTURES[2]]:
                if conv_type is not self.OPTIONS_CONVERGERS[2]:
                    log_statements.append(['WARNING C02', 'Convergence type %s does not match with architecture %s.' % \
                          (conv_type, mdao_arch)])
                    formulation_check = False
            # match for unconverged-MDA, IDF, unconverged-OPT, unconverged-DOE
            if mdao_arch in [self.OPTIONS_ARCHITECTURES[0], self.OPTIONS_ARCHITECTURES[4],
                             self.OPTIONS_ARCHITECTURES[5]]:
                if allow_unconverged_couplings:
                    if conv_type not in self.OPTIONS_CONVERGERS[:2]:
                        log_statements.append(['WARNING C03', 'Convergence type %s does not match with architecture %s.' % \
                              (conv_type, mdao_arch)])
                        log_statements.append(['WARNING C04', 'As unconverged couplings are allowed, a convergence method has to be ' \
                              'selected.'])
                        formulation_check = False
                else:
                    if conv_type is not self.OPTIONS_CONVERGERS[2]:
                        log_statements.append(['WARNING C05', 'Convergence type %s does not match with architecture %s.' % \
                              (conv_type, mdao_arch)])
                        formulation_check = False
        # For architectures using convergence, check whether this is necessary
        if formulation_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            if mdao_arch == self.OPTIONS_ARCHITECTURES[1]: # converged-MDA
                if not self.check_for_coupling(coup_funcs, only_feedback=
                                               True if conv_type == self.OPTIONS_CONVERGERS[1] else False):
                    log_statements.append(['WARNING C06', 'Inconsistent problem formulation, expected coupling missing.'])
                    log_statements.append(['WARNING C06', 'Architecture should be set to "unconverged-MDA".'])
                    formulation_check = False
            if mdao_arch == self.OPTIONS_ARCHITECTURES[3]:  # MDF
                if not self.check_for_coupling(coup_funcs, only_feedback=
                                               True if conv_type == self.OPTIONS_CONVERGERS[1] else False):
                    log_statements.append(['WARNING C06', 'Inconsistent problem formulation, expected coupling missing.'])
                    log_statements.append(['WARNING C06', 'Architecture should be set to "unconverged-OPT".'])
                    formulation_check = False
            if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:  # IDF
                if not self.check_for_coupling(coup_funcs, only_feedback=False):
                    log_statements.append(['WARNING C06', 'Inconsistent problem formulation, expected coupling missing.'])
                    log_statements.append(['WARNING C06', 'Architecture should be set to "unconverged-OPT".'])
                    formulation_check = False
            if mdao_arch == self.OPTIONS_ARCHITECTURES[6]: # converged-DOE
                if not self.check_for_coupling(coup_funcs, only_feedback=
                                               True if conv_type == self.OPTIONS_CONVERGERS[1] else False):
                    log_statements.append(['WARNING C06', 'Inconsistent problem formulation, expected coupling missing.'])
                    log_statements.append(['WARNING C06', 'Architecture should be set to "unconverged-DOE".'])
                    formulation_check = False
        # For architectures not using convergence, check whether this is allowed
        if formulation_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            # unconverged-MDA, unconverged-OPT, unconverged-DOE
            if mdao_arch in get_list_entries(self.OPTIONS_ARCHITECTURES,0,4,5):
                if not allow_unconverged_couplings:
                    if self.check_for_coupling(coup_funcs, only_feedback=True):
                        log_statements.append(['WARNING C07', 'Inconsistent problem formulation, no feedback coupling was expected.'])
                        log_statements.append(['WARNING C07', 'Architecture should be set to something using convergence (e.g. MDF, IDF).'])
                        log_statements.append(['WARNING C07', 'Or setting allow_unconverged_couplings should be set to True.'])
                        formulation_check = False
                else:
                    if not self.check_for_coupling(coup_funcs, only_feedback=
                    True if conv_type == self.OPTIONS_CONVERGERS[1] else False):
                        log_statements.append(['WARNING C06', 'Inconsistent problem formulation, expected coupling missing.'])
                        log_statements.append(['WARNING C06', 'Architecture should be set to unconverged variant without convergence type.'])
                        formulation_check = False

        # Check the feedforwardness of the pre-coupling functions
        if formulation_check:
            precoup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[0]]
            if self.check_for_coupling(precoup_funcs, only_feedback=True):
                log_statements.append(['WARNING C08', 'Pre-coupling functions contain feedback variables.'])
                log_statements.append(['WARNING C08', 'Pre-coupling functions should be adjusted.'])
                formulation_check = False
        # Check whether the necessary variables have been marked with the problem_role attribute
        if formulation_check:
            if mdao_arch in self.OPTIONS_ARCHITECTURES[2:5]: # IDF, MDF, unconverged-OPT
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                if len(des_var_nodes) == 0:
                    log_statements.append(["WARNING C09", "No design variables are specified. Use the 'problem_role' attribute for this."])
                    formulation_check = False
                # Check the design variables connections
                for des_var_node in des_var_nodes:
                    des_var_sources = self.get_sources(des_var_node)
                    if not set(des_var_sources).issubset(precoup_funcs):
                        log_statements.append(["WARNING C10", "Design variable %s has a source after the pre-coupling functions."\
                              % des_var_node])
                        log_statements.append(["WARNING C10", "Adjust design variables or function order to solve this."])
                        formulation_check = False
                    if self.out_degree(des_var_node) == 0:
                        log_statements.append(["WARNING C11", "Design variable %s does not have any targets." % des_var_node])
                        log_statements.append(["WARNING C11", "Reconsider design variable selection."])
                        formulation_check = False
                constraint_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[2]])
                objective_node = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
                if len(objective_node) != 1:
                    log_statements.append(["WARNING C12", "%d objective variables are specified. Only one objective node is allowed."\
                          % len(objective_node)])
                    log_statements.append(["WARNING C12", "Use the 'problem_role' attribute for this."])
                    formulation_check = False
                constraint_functions = list()
                for idx, node in enumerate(objective_node + constraint_nodes):
                    if self.in_degree(node) != 1:
                        log_statements.append(["WARNING C13", "Invalid indegree of %d, while it should be 1." % self.in_degree(node)])
                        formulation_check = False
                    if self.out_degree(node) != 0:
                        log_statements.append(["WARNING C13", "Invalid outdegree of %d, while it should be 0." % self.out_degree(node)])
                        formulation_check = False
                    if idx == 0:
                        objective_function = list(self.in_edges(node))[0][0]
                    elif not (list(self.in_edges(node))[0][0] in set(constraint_functions)):
                        constraint_functions.append(list(self.in_edges(node))[0][0])
                if formulation_check:
                    # Check that the objective function is unique (not also a constraint function)
                    if objective_function in constraint_functions:
                        log_statements.append(["WARNING C14", "Objective function should be a separate function."])
                        formulation_check = False
                    optimizer_functions = [objective_function] + constraint_functions
                    # Check that all optimizer function are post-coupling functions for IDF and MDF
                    if mdao_arch in self.OPTIONS_ARCHITECTURES[2:4]:
                        func_cats = self.graph['problem_formulation']['function_ordering']
                        diff = set(optimizer_functions).difference(func_cats[self.FUNCTION_ROLES[2]])
                        coup_check = self.check_for_coupling(optimizer_functions, only_feedback=False)
                        if diff:
                            log_statements.append(["WARNING C15", "Not all optimizer functions are not post-coupling functions, " \
                                  "namely: %s." % diff])
                            formulation_check = False
                        if coup_check:
                            log_statements.append(["WARNING C16", "The optimizer functions %s are not independent of each other." % \
                                  optimizer_functions])
                            formulation_check = False
            if mdao_arch in self.OPTIONS_ARCHITECTURES[:2] + self.OPTIONS_ARCHITECTURES[5:7]:
                # unc-MDA, con-MDA, unc-DOE, con-DOE
                # Check whether quantities of interest have been defined.
                qoi_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[3]])
                if len(qoi_nodes) == 0:
                    log_statements.append(["WARNING C17", "No quantities of interest are specified. Use the 'problem_role' attribute for" \
                          " this."])
                    formulation_check = False
            if mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]: # unc-DOE, con-DOE
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                if len(des_var_nodes) == 0:
                    log_statements.append(["WARNING C18", "No design variables are specified. Use the 'problem_role' attribute for this."])
                    formulation_check = False
                else:
                    # If custom table, check the samples
                    if self.graph['problem_formulation']['doe_settings']['doe_method'] == self.OPTIONS_DOE_METHODS[3]:
                        all_samples = []
                        for des_var_node in des_var_nodes:
                            if 'samples' not in self.node[des_var_node]:
                                log_statements.append(["WARNING C19", "samples attributes is missing for design variable node %s." % \
                                      des_var_node])
                                formulation_check = False
                            else:
                                all_samples.append(self.node[des_var_node]['samples'])
                        sample_lengths = [len(item) for item in all_samples]
                        # Check whether all samples have the same length
                        if not sample_lengths.count(sample_lengths[0]) == len(sample_lengths):
                            log_statements.append(["WARNING C20", "not all given samples have the same length, this is mandatory."])
                            formulation_check = False

        if formulation_check:
            log_statements.append(['Problem formulation check', 'done!'])
        else:
            log_statements.append(['Problem formulation check', 'done with warnings!'])
            return (formulation_check, log_statements)

        return (True, log_statements)
