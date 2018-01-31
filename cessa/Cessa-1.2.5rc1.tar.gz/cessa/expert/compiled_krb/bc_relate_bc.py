# bc_relate_bc.py

from pyke import contexts, pattern, bc_rule

pyke_version = '1.1.1'
compiler_version = 1

def get_clabel_list(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'clabel', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.get_clabel_list: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def get_all_args(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'arg_list', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.get_all_args: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def get_all_value(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'all_value', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.get_all_value: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def get_type(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'arg_type', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.get_type: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def get_index(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'arg_index', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.get_index: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def get_macro_value(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('macro', 'define', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.get_macro_value: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def related_args(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'arg_related', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.related_args: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def strict_mode_1(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        value_list = []
        with engine.prove('argument', 'relevant', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_2:
          for x_2 in gen_2:
            assert x_2 is None, \
              "bc_relate.strict_mode_1: got unexpected plan from when clause 2"
            with engine.prove('syscall', 'all_value', context,
                              (rule.pattern(2),
                               rule.pattern(3),)) \
              as gen_3:
              for x_3 in gen_3:
                assert x_3 is None, \
                  "bc_relate.strict_mode_1: got unexpected plan from when clause 3"
                for python_ans in \
                     context.lookup_data('value_relevant_tuple'):
                  mark4 = context.mark(True)
                  if rule.pattern(4).match_data(context, context, python_ans):
                    context.end_save_all_undo()
                    for python_ans in \
                         context.lookup_data('value_total_tuple'):
                      mark5 = context.mark(True)
                      if rule.pattern(4).match_data(context, context, python_ans):
                        context.end_save_all_undo()
                        value_list.append(context.lookup_data('value'))
                      else: context.end_save_all_undo()
                      context.undo_to_mark(mark5)
                  else: context.end_save_all_undo()
                  context.undo_to_mark(mark4)
                mark7 = context.mark(True)
                if rule.pattern(5).match_data(context, context,
                        tuple(value_list)):
                  context.end_save_all_undo()
                  rule.rule_base.num_bc_rule_successes += 1
                  yield
                else: context.end_save_all_undo()
                context.undo_to_mark(mark7)
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def strict_mode_2(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('argument', 'relevant', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.strict_mode_2: got unexpected plan from when clause 1"
            with engine.prove('syscall', 'all_value', context,
                              (rule.pattern(2),
                               rule.pattern(3),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "bc_relate.strict_mode_2: got unexpected plan from when clause 2"
                for python_ans in \
                     context.lookup_data('value_relevant_tuple'):
                  mark3 = context.mark(True)
                  if rule.pattern(4).match_data(context, context, python_ans):
                    context.end_save_all_undo()
                    for python_ans in \
                         context.lookup_data('value_total_tuple'):
                      mark4 = context.mark(True)
                      if rule.pattern(4).match_data(context, context, python_ans):
                        context.end_save_all_undo()
                        rule.rule_base.num_bc_rule_successes += 1
                        yield
                      else: context.end_save_all_undo()
                      context.undo_to_mark(mark4)
                  else: context.end_save_all_undo()
                  context.undo_to_mark(mark3)
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def loose_mode_1(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'all_value', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.loose_mode_1: got unexpected plan from when clause 1"
            value_set = set(context.lookup_data('value_total_tuple'))
            with engine.prove('argument', 'conflicting', context,
                              (rule.pattern(2),
                               rule.pattern(3),)) \
              as gen_3:
              for x_3 in gen_3:
                assert x_3 is None, \
                  "bc_relate.loose_mode_1: got unexpected plan from when clause 3"
                for python_ans in \
                     context.lookup_data('value_conflicting_value'):
                  mark4 = context.mark(True)
                  if rule.pattern(4).match_data(context, context, python_ans):
                    context.end_save_all_undo()
                    value_set.remove(context.lookup_data('value'))
                  else: context.end_save_all_undo()
                  context.undo_to_mark(mark4)
                mark6 = context.mark(True)
                if rule.pattern(5).match_data(context, context,
                        tuple(value_set)):
                  context.end_save_all_undo()
                  rule.rule_base.num_bc_rule_successes += 1
                  yield
                else: context.end_save_all_undo()
                context.undo_to_mark(mark6)
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def loose_mode_2(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                   pat.match_pattern(context, context,
                                     arg, arg_context),
                 patterns,
                 arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('syscall', 'all_value', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "bc_relate.loose_mode_2: got unexpected plan from when clause 1"
            with engine.prove('argument', 'conflicting', context,
                              (rule.pattern(2),
                               rule.pattern(3),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "bc_relate.loose_mode_2: got unexpected plan from when clause 2"
                for python_ans in \
                     context.lookup_data('value_total_tuple'):
                  mark3 = context.mark(True)
                  if rule.pattern(4).match_data(context, context, python_ans):
                    context.end_save_all_undo()
                    if context.lookup_data('value') not in context.lookup_data('value_conflicting_value'):
                      rule.rule_base.num_bc_rule_successes += 1
                      yield
                  else: context.end_save_all_undo()
                  context.undo_to_mark(mark3)
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def populate(engine):
  This_rule_base = engine.get_create('bc_relate')
  
  bc_rule.bc_rule('get_clabel_list', This_rule_base, 'clabel_list',
                  get_clabel_list, None,
                  (contexts.variable('syscall'),
                   contexts.variable('clabel_tuple'),),
                  (),
                  (contexts.variable('syscall'),
                   contexts.variable('clabel_tuple'),))
  
  bc_rule.bc_rule('get_all_args', This_rule_base, 'arg_list',
                  get_all_args, None,
                  (contexts.variable('syscall'),
                   contexts.variable('argument_tuple'),),
                  (),
                  (contexts.variable('syscall'),
                   contexts.variable('argument_tuple'),))
  
  bc_rule.bc_rule('get_all_value', This_rule_base, 'all_value',
                  get_all_value, None,
                  (contexts.variable('argument'),
                   contexts.variable('value_tuple'),),
                  (),
                  (contexts.variable('argument'),
                   contexts.variable('value_tuple'),))
  
  bc_rule.bc_rule('get_type', This_rule_base, 'arg_type',
                  get_type, None,
                  (contexts.variable('argument'),
                   contexts.variable('type'),),
                  (),
                  (contexts.variable('argument'),
                   contexts.variable('type'),))
  
  bc_rule.bc_rule('get_index', This_rule_base, 'arg_index',
                  get_index, None,
                  (contexts.variable('argument'),
                   contexts.variable('index'),),
                  (),
                  (contexts.variable('argument'),
                   contexts.variable('index'),))
  
  bc_rule.bc_rule('get_macro_value', This_rule_base, 'macro_value',
                  get_macro_value, None,
                  (contexts.variable('macro'),
                   contexts.variable('value'),),
                  (),
                  (contexts.variable('macro'),
                   contexts.variable('value'),))
  
  bc_rule.bc_rule('related_args', This_rule_base, 'related_args',
                  related_args, None,
                  (contexts.variable('arg1'),
                   contexts.variable('arg2'),),
                  (),
                  (contexts.variable('arg1'),
                   contexts.variable('arg2'),))
  
  bc_rule.bc_rule('strict_mode_1', This_rule_base, 'accurate_value_tuple',
                  strict_mode_1, None,
                  (contexts.variable('argument'),
                   contexts.variable('label'),
                   contexts.variable('value_tuple'),),
                  (),
                  (contexts.variable('label'),
                   contexts.variable('value_relevant_tuple'),
                   contexts.variable('argument'),
                   contexts.variable('value_total_tuple'),
                   contexts.variable('value'),
                   contexts.variable('value_tuple'),))
  
  bc_rule.bc_rule('strict_mode_2', This_rule_base, 'accurate_value',
                  strict_mode_2, None,
                  (contexts.variable('argument'),
                   contexts.variable('label'),
                   contexts.variable('value'),),
                  (),
                  (contexts.variable('label'),
                   contexts.variable('value_relevant_tuple'),
                   contexts.variable('argument'),
                   contexts.variable('value_total_tuple'),
                   contexts.variable('value'),))
  
  bc_rule.bc_rule('loose_mode_1', This_rule_base, 'possible_value_tuple',
                  loose_mode_1, None,
                  (contexts.variable('argument'),
                   contexts.variable('label'),
                   contexts.variable('value_tuple'),),
                  (),
                  (contexts.variable('argument'),
                   contexts.variable('value_total_tuple'),
                   contexts.variable('label'),
                   contexts.variable('value_conflicting_value'),
                   contexts.variable('value'),
                   contexts.variable('value_tuple'),))
  
  bc_rule.bc_rule('loose_mode_2', This_rule_base, 'possible_value',
                  loose_mode_2, None,
                  (contexts.variable('argument'),
                   contexts.variable('label'),
                   contexts.variable('value'),),
                  (),
                  (contexts.variable('argument'),
                   contexts.variable('value_total_tuple'),
                   contexts.variable('label'),
                   contexts.variable('value_conflicting_value'),
                   contexts.variable('value'),))


Krb_filename = '../bc_relate.krb'
Krb_lineno_map = (
    ((14, 18), (2, 2)),
    ((20, 26), (4, 4)),
    ((39, 43), (7, 7)),
    ((45, 51), (9, 9)),
    ((64, 68), (12, 12)),
    ((70, 76), (14, 14)),
    ((89, 93), (17, 17)),
    ((95, 101), (19, 19)),
    ((114, 118), (22, 22)),
    ((120, 126), (24, 24)),
    ((139, 143), (27, 27)),
    ((145, 151), (29, 29)),
    ((164, 168), (32, 32)),
    ((170, 176), (34, 34)),
    ((189, 193), (37, 37)),
    ((195, 195), (39, 39)),
    ((196, 202), (40, 40)),
    ((203, 209), (41, 41)),
    ((211, 211), (43, 43)),
    ((216, 216), (44, 44)),
    ((220, 220), (45, 45)),
    ((227, 227), (46, 46)),
    ((243, 247), (49, 49)),
    ((249, 255), (51, 51)),
    ((256, 262), (52, 52)),
    ((264, 264), (53, 53)),
    ((269, 269), (54, 54)),
    ((289, 293), (57, 57)),
    ((295, 301), (59, 59)),
    ((302, 302), (60, 60)),
    ((303, 309), (61, 61)),
    ((311, 311), (63, 63)),
    ((315, 315), (64, 64)),
    ((320, 320), (65, 65)),
    ((336, 340), (68, 68)),
    ((342, 348), (70, 70)),
    ((349, 355), (71, 71)),
    ((357, 357), (72, 72)),
    ((361, 361), (73, 73)),
)
