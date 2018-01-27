#!/usr/bin/env python
# -*- coding: utf-8 -*-
import oerplib
from os0 import os0
# import pdb


__version__ = "0.1.6.2"
STATES_2_DRAFT = ['open', 'paid', 'posted']
STS_FAILED = 1
STS_SUCCESS = 0


def msg_log(ctx, level, msg):
    print msg
    fd = open('prj_acc_filter.log', 'a')
    fd.write(os0.b(msg) + '\n')
    fd.close()


def add_on_account(acc_balance, level, code, debit, credit):
    if level not in acc_balance:
        acc_balance[level] = {}
    if code:
        if code in acc_balance[level]:
            acc_balance[level][code] += debit
            acc_balance[level][code] -= credit
        else:
            acc_balance[level][code] = debit
            acc_balance[level][code] -= credit


def act_check_balance(oerp, ctx):
    company_id = ctx['company_id']
    acc_balance = {}
    acc_partners = {}
    STATES = STATES_2_DRAFT
    if ctx.get('draft_recs', False):
        STATES.append('draft')
    move_line_ids = oerp.search('account.move.line',
                                [('move_id', 'in', ctx['domain'])])
    num_moves = len(move_line_ids)
    move_ctr = 0
    for move_line_id in move_line_ids:
        move_line_obj = oerp.browse('account.move.line', move_line_id)
        move_ctr += 1
        print "Move    ", move_ctr, '/', num_moves
        warn_rec = False
        move_hdr_id = move_line_obj.move_id.id
        account_obj = move_line_obj.account_id
        account_tax_obj = move_line_obj.account_tax_id
        journal_obj = move_line_obj.journal_id
        acctype_id = account_obj.user_type.id
        acctype_obj = oerp.browse('account.account.type', acctype_id)
        if acctype_obj.report_type not in ("asset", "liability",
                                           "income", "expense"):
            warn_rec = "Untyped"
        if account_obj.parent_id:
            parent_account_obj = account_obj.parent_id
            parent_acctype_id = parent_account_obj.user_type.id
            parent_acctype_obj = oerp.browse('account.account.type',
                                             parent_acctype_id)
            parent_code = parent_account_obj.code
        else:
            parent_account_obj = None
            parent_acctype_id = 0
            parent_acctype_obj = None
            parent_code = None
            warn_rec = 'Orphan'
        if parent_acctype_obj and\
                parent_acctype_obj.report_type and\
                parent_acctype_obj.report_type != 'none':
            if parent_acctype_obj.report_type in ("asset",
                                                  "liability",
                                                  "income",
                                                  "expense") and \
                    acctype_obj.report_type != parent_acctype_obj.report_type:
                warn_rec = "Mismatch"

        code = account_obj.code
        clf3 = acctype_obj.name
        clf = acctype_obj.report_type
        if clf == "asset":
            clf2 = "attivo"
            clf1 = "patrimoniale"
        elif clf == "liability":
            clf2 = "passivo"
            clf1 = "patrimoniale"
        elif clf == "income":
            clf2 = "ricavi"
            clf1 = "conto economico"
        elif clf == "expense":
            clf2 = "costi"
            clf1 = "conto economico"
        else:
            clf2 = "unknown"
            clf1 = "unknown"

        if (account_obj.company_id.id != company_id):
            msg = u"Invalid company account {0} in {1:>6} {2}".format(
                os0.u(code),
                move_line_id,
                os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if (account_tax_obj and account_tax_obj.company_id.id != company_id):
            msg = u"Invalid company account tax {0} in {1:>6} {2}".format(
                os0.u(code),
                move_line_id,
                os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if (journal_obj and journal_obj.company_id.id != company_id):
            msg = u"Invalid company journal {0} in {1:>6} {2}".format(
                os0.u(code),
                move_line_id,
                os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
        if move_line_obj.partner_id and \
                move_line_obj.partner_id.id:
            partner_id = move_line_obj.partner_id.id
            if clf3 == "Crediti":
                kk = 'C'
            elif clf3 == "Debiti":
                kk = 'S'
            else:
                kk = 'X'
            kk = kk + '\n' + code + '\n' + str(partner_id)
            if kk not in acc_partners:
                acc_partners[kk] = 0
            acc_partners[kk] += move_line_obj.debit
            acc_partners[kk] -= move_line_obj.credit

        level = '9'
        add_on_account(acc_balance,
                       level,
                       code,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '8'
        add_on_account(acc_balance,
                       level,
                       parent_code,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '4'
        add_on_account(acc_balance,
                       level,
                       clf3,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '2'
        add_on_account(acc_balance,
                       level,
                       clf2,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '1'
        add_on_account(acc_balance,
                       level,
                       clf1,
                       move_line_obj.debit,
                       move_line_obj.credit)

        level = '0'
        add_on_account(acc_balance,
                       level,
                       '_',
                       move_line_obj.debit,
                       move_line_obj.credit)

        if warn_rec:
            msg = u"Because {0:8} look at {1:>6}/{2:>6} record {3}".format(
                warn_rec,
                move_hdr_id,
                move_line_id,
                os0.u(move_line_obj.ref))
            msg_log(ctx, ctx['level'] + 1, msg)
            warn_rec = False

    if '0' in acc_balance:
        for level in ('0', '1', '2', '4', '8', '9'):
            if level == '0':
                ident = "- {0:<10}".format('GT')
            elif level == '1':
                ident = " - {0:<9}".format('TOTALE')
            elif level == '2':
                ident = "  - {0:<8}".format('Totale')
            elif level == '4':
                ident = "   - {0:<7}".format('Grp')
            elif level == '8':
                ident = "    - {0:<6}".format('Mastro')
            else:
                ident = "     - {0:<5}".format('conto')
            crd_amt = 0.0
            dbt_amt = 0.0
            for sublevel in acc_balance[level]:
                if acc_balance[level][sublevel] > 0:
                    msg = u"{0} {1:<16} {2:11.2f}".format(
                        os0.u(ident),
                        os0.u(sublevel),
                        acc_balance[level][sublevel])
                    msg_log(ctx, ctx['level'], msg)
                    crd_amt += acc_balance[level][sublevel]
                elif acc_balance[level][sublevel] < 0:
                    msg = u"{0} {1:<16} {2:11}{3:11.2f}".format(
                        os0.u(ident),
                        os0.u(sublevel),
                        '',
                        -acc_balance[level][sublevel])
                    msg_log(ctx, ctx['level'], msg)
                    dbt_amt -= acc_balance[level][sublevel]
                else:
                    msg = u"{0} {1:<16} {2:11.2f}{3:11.2f}".format(
                        os0.u(ident),
                        os0.u(sublevel),
                        0,
                        0)
                    msg_log(ctx, ctx['level'], msg)
            msg = u"{0} {1:<16} {2:11.2f}{3:11.2f}".format(
                os0.u(ident),
                '---------------',
                crd_amt,
                dbt_amt)
            msg_log(ctx, ctx['level'], msg)
        level = '9'
        for kk in sorted(acc_partners):
            if acc_partners[kk] != 0.0:
                partner_id = int(kk.split('\n')[2])
                partner_obj = oerp.browse('res.partner', partner_id)
                msg = u"{0:<16} {1:<60} {2:11.2f}".format(
                    os0.u(kk.replace('\n', '.')),
                    os0.u(partner_obj.name),
                    acc_partners[kk])
                msg_log(ctx, ctx['level'], msg)
    return STS_SUCCESS


oerp = oerplib.OERP()
try:
    fd = open('./inv2draft_n_restore.conf', 'r')
    lines = fd.read().split('\n')
    for line in lines:
        tkn = line.split('=')
        if tkn[0] == 'login_user':
            user = tkn[1]
        elif tkn[0] == 'login_password':
            passwd = tkn[1]
        elif tkn[0] == 'db_name':
            database = tkn[1]
    fd.close()
except:
    database = raw_input('database? ')
    user = raw_input('username? ')
    passwd = raw_input('password? ')
uid = oerp.login(user=user,
                 passwd=passwd, database=database)
fd = open('./inv2draft_n_restore.conf', 'w')
fd.write('login_user=%s\n' % user)
fd.write('login_password=%s\n' % passwd)
fd.write('db_name=%s\n' % database)
fd.close()


ctx = {}
ctx['level'] = 4
ctx['dry_run'] = False
ctx['company_id'] = 3
print "Create account filter on project - %s" % __version__

model = 'ir.filters'
pids = oerp.search(model, [('name', '=like', 'Bilancio patr. progetto %')])
if len(pids) == 0:
    print "No filter found!"
    exit(1)
eids = oerp.search(model, [('name', '=like', 'Risultato progetto %')])
if len(eids) == 0:
    print "No filter found!"
    exit(1)

PRJIDS = {'007': 'EM5',
          '014': 'Aracne',
          '050': 'SOSnet',
          '112': 'ConnectVET',
          '164': 'EURehabChildren',
          '175': 'EUM/36057',
          '186': 'EM6',
          '187': 'CB4LLP',
          '188': 'EM7',
          '189': 'SSA',
          '191': 'EM8',
          }

project_sfx = raw_input('Project suffix: ')
if not project_sfx:
    exit(1)
if project_sfx in PRJIDS:
    project_name = PRJIDS[project_sfx]
else:
    project_name = raw_input('Project name: ')
if not project_name:
    exit(1)
year = raw_input('year: ')
if not year:
    year = '2016'

company_id = ctx['company_id']
p_filter = "[('company_id', '=', %d), " % company_id
g_filter = p_filter
sqlcmd = "select l.move_id from account_move_line l, account_account a"
sqlcmd += " where l.account_id=a.id and l.company_id=%d " % company_id
if year == '*':
    p_title = 'Bilancio patr. progetto %s' % project_name
    ctx['date_start'] = '2000-01-01'
    ctx['date_stop'] = '2099-12-31'
else:
    p_title = 'Bilancio patr. progetto %s anno %s' % (project_name, year)
    p_filter += "('date', '>=', '%s-01-01'), " % year
    p_filter += "('date', '<=', '%s-12-31'), " % year
    ctx['date_start'] = '%s-01-01' % year
    ctx['date_stop'] = '%s-12-31' % year
    sqlcmd += " and l.date>='%s-01-01' " % year
    sqlcmd += " and l.date<='%s-12-31' " % year
    g_filter = p_filter
p_filter += "'|', ('account_id', '=', '140%s'), " % project_sfx
p_filter += "'|', ('account_id', '=', '244%s'), " % project_sfx
p_filter += "('account_id', '=', '165%s')]" % project_sfx
g_filter += "'|', ('account_id', '=', '140%s'), " % project_sfx
g_filter += "'|', ('account_id', '=', '244%s'), " % project_sfx
g_filter += "'|', ('account_id', '=', '165%s'), " % project_sfx
sqlcmd += " and a.code in ("
sqlcmd += "'140%s'," % project_sfx
sqlcmd += "'244%s'," % project_sfx
sqlcmd += "'165%s'," % project_sfx
print p_title
print p_filter

e_filter = "[('company_id', '=', %d), " % company_id
if year == '*':
    e_title = 'Risultato progetto %s' % project_name
else:
    e_title = 'Risultato progetto %s anno %s' % (project_name, year)
    e_filter += "('date', '>=', '%s-01-01'), " % year
    e_filter += "('date', '<=', '%s-12-31'), " % year
e_filter += "'|', ('account_id', '=', '330%s'), " % project_sfx
e_filter += "'|', ('account_id', '=', '412%s'), " % project_sfx
e_filter += "'|', ('account_id', '=', '310%s'), " % project_sfx
e_filter += "('account_id', '=', '780%s')]" % project_sfx
g_filter += "'|', ('account_id', '=', '330%s'), " % project_sfx
g_filter += "'|', ('account_id', '=', '412%s'), " % project_sfx
g_filter += "'|', ('account_id', '=', '310%s'), " % project_sfx
g_filter += "('account_id', '=', '780%s')]" % project_sfx
sqlcmd += "'330%s'," % project_sfx
sqlcmd += "'412%s'," % project_sfx
sqlcmd += "'310%s'," % project_sfx
sqlcmd += "'780%s'" % project_sfx
print e_title
print e_filter

# ir_filters = oerp.browse(model, pids[0])
oerp.write(model, pids, {'name': p_title, 'domain': p_filter})
oerp.write(model, eids, {'name': e_title, 'domain': e_filter})
print "-----------------------"
print g_filter
sqlcmd += ") group by l.move_id;"
print sqlcmd
move_line_ids = oerp.search('account.move.line',
                            eval(g_filter))
move_ids = []
for move_line_id in move_line_ids:
    move_line_obj = oerp.browse('account.move.line', move_line_id)
    move_id = move_line_obj.move_id.id
    if move_id not in move_ids:
        move_ids.append(move_id)
ctx['domain'] = move_ids
act_check_balance(oerp, ctx)
