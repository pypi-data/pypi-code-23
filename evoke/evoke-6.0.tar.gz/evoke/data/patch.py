"""
 patches application data automatically on startup, according to evoke version number

 - 2 stage process: pre_schema and post_schema, both called from app.py
 - 
"""

from .DB import execute
from evoke.lib import Error, safeint


class InvalidDatabaseError(Error):
    'INVALID DATABASE: database "%s" exists but has no Var table and/or evoke-version entry'


def pre_schema_patch(version, config):
    ""


#  if version<1974:
#   do("rename table `%s`.accounts to `%s`.pages" % (config.database,config.database))
#  if version<1977:
#   do("drop table `%s`.transactions" % config.database)
#   do("drop table `%s`.contacts" % config.database)
#   do("alter table `%s`.users change column account page int default 1" % config.database)
#  if version<2001:
#   do("insert into `%s`.pages (parent,`group`,name,kind,who,lineage) values (1,4,'site','site',4,'.1.')" % config.database)
#  if version<2470:
#   do("update `%s`.pages set kind='group' where kind='community'" % config.database)
#   do("update `%s`.pages set parent=4 where uid>2 and kind='group'" % config.database)
#  if version<2682:
#   do("update `%s`.pages set text='publish_filepath=~\n' where kind='site' and `group`=4" % config.database) # home site default filepath
#  if version<2709:
#   do("update `%s`.pages set parent=4 where kind='site' and `group`=4 and parent=1 and name!='site'"% config.database) # front site belongs to admin
#  if version<2710:
#   do("update `%s`.pages i,`%s`.pages p set i.`group`=p.`group` where i.kind='image' and i.`group`=0 and p.uid=i.parent" % (config.database,config.database))
#  if version<2828: # make unicode compatible
#    do("alter database `%s` charset=utf8" % config.database)
#    for t in [t["Tables_in_%s" % config.database] for t in execute("show tables from `%s`" % config.database)]:
#      for (c,typ) in [(c["Field"],c["Type"]) for c in execute("show columns  from `%s`.`%s`" % (config.database,t))]:
#        if typ=='text':
#          do("alter table `%s`.`%s` modify column `%s` mediumtext" % (config.database,t,c))
#      do("alter table `%s`.`%s` convert to charset utf8" % (config.database,t))


def post_schema_patch(version, app):
    ""


#  if version<2199: # init user dates
#    for u in app.classes['User'].list(where='page>1'):
#      u.when=u.page.when
#      u.flush()
#  if version<2910: # fix article seqs
#    app.classes['Page'].patch_seq()
#    print 'PATCH: seq patched'
#  if version<2965: # fix site prefs
#    for p in app.classes["Page"].list(kind='site'):
#      p.prefs=p.text
#      p.text=''
#      p.flush()
#    print 'PATCH: site prefs patched'

def evoke_version(app):
    """single version number combining the major and minor parts
    (for internal use only, allowing simple numerical comparison)
    """
    major,minor=app.Config.evoke_version.split(".")
    return int(major)*1000000+int(minor)

def pre_schema(app):
    "database adjustments prior to loading the schema"
    global version
#    print('checking patches for "%s"' % app.Config.appname)
    config = app.Config
    version = evoke_version(app)
    try:
        res = execute("select * from `%s`.vars where name='evoke-version'" %
                      config.database)
    except:
        if config.database in [
                x["Database"] for x in execute("show databases")
        ]:
            print([x["Database"] for x in execute("show databases")])
            raise InvalidDatabaseError(
                config.database, )  # we have an invalid database
        else:  # we have no database, so it will be created by schema
            return
    if not res:  #initial patch - ie create var
        pre_schema_patch(0, config)
        execute(
            "insert into `%s`.vars (name,value,comment) values ('evoke-version',%s,'used for patching')"
            % (config.database, version))
        return
    var_version = res[0]['value']
    if var_version < version:
        pre_schema_patch(version, config)
        #set the var textvalue to version number to indicate we are not finished 
        # - in case the schema process crashes (so we don't attempt the patch again - safety first!)
        execute(
            "update `%s`.vars set value=%s,textvalue='%s' where name='evoke-version'"
            % (config.database, version, version))


def post_schema(app):
    "database adjustments after the schema is loaded"
    global version
    vars = app.classes['Var']
    var_version = vars.fetch('evoke-version')
    z = safeint(var_version.textvalue)
    if z:  #if there was a crash after pre-schema patching, z will now contain the version number we were patching to, otherwise z will be 0
        version = z  #reset version to pre-crash version
    if (var_version.value < evoke_version(app)):
        post_schema_patch(version, app)
    set_version(app)


def set_version(app):
    "updates or adds the evoke-version - requires schema to be in place"
    config = app.Config
    vars = app.classes['Var']
    var_version = vars.fetch('evoke-version')
    newversion=evoke_version(app)    # eg 5000123
    version=app.Config.evoke_version # eg 5.123
    if not var_version.value:
        vars.add(
            'evoke-version',
            newversion,
            textvalue='valid',
            datevalue='',
            comment='used for patching')  #create version var, dated today
        print("PATCH:version is %s" % version)
    elif var_version.value < newversion:
        vars.amend(
            'evoke-version',
            newversion,
            textvalue='valid',
            datevalue='')  #update version, text and date
        print("PATCH:version updated to %s" % version)
    elif var_version.textvalue != 'valid':
        vars.amend(
            'evoke-version', textvalue='valid',
            datevalue='')  #update text and date
        print("PATCH:version updated to %s" % version)


def do(sql):
    execute(sql)
    print('PATCH:' + sql)
