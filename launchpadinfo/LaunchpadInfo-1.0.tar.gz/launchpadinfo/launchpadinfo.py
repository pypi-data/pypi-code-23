from launchpadlib.launchpad import Launchpad
launchpad = Launchpad.login_with('hello-world', 'production')
me=launchpad.me
jabber=[]
for i in me.jabber_ids:
  jabber.append(i)
irc=[]
for i in me.irc_nicknames:
  irc.append(i)
lang=[]
for i in me.languages:
  lang.append(i)
gpg=[]
for i in me.gpg_keys:
  gpg.append(i)
ssh=[]
for i in me.sshkeys:
  ssh.append(i)
print('Hello, %s!' % me.display_name)
print('Account Details:')
print('###############')
print('Display name: %s'% me.display_name)
print('Description: %s'% me.description)
print('Launchpad Id: %s'% me.name)
print('Preferred Email: %s'% me.preferred_email_address)
print('Jabber: %s'% jabber)
print('OpenID login: https://launchpad.net/~%s'% me.name)
print('Member since: %s'% me.date_created)
print('Signed Ubuntu Code of Conduct: %s'% me.is_ubuntu_coc_signer)
print('IRC: %s'% irc)
print('Languages: %s'% lang)
print('Karma: %s'% me.karma)
print('OpenPGP keys: %s'% gpg)
print('SSH keys: %s'% ssh)
print('Time zone: %s'% me.time_zone)
print('###############')
edit=raw_input('Do you want to edit anything? (Please use the exact keyword as in program, type n to skip) :')
if edit=='n':
  print('Skipped!')
elif edit=='Display name':
  me.display_name=raw_input('Enter the new Display name :')
  me.lp_save()
  print('Display name saved')
elif edit=='Description':
  me.description=raw_input('Enter the new Description :')
  me.lp_save()
  print('Description saved')
elif edit=='Jabber':
  print('Please go to https://launchpad.net/~%s/+editjabberids to do so'% me.name)
elif edit=='IRC':
  print('Please go to https://launchpad.net/~%s/+editircnicknames to do so'% me.name)
elif edit=='Languages':
  print('Please go to https://launchpad.net/~%s/+editlanguages to do so'% me.name)
elif edit=='OpenPGP keys':
  print('Please go to https://launchpad.net/~%s/+editpgpkeys to do so'% me.name)
elif edit=='SSH keys':
  print('Please go to https://launchpad.net/~%s/++editsshkeys to do so'% me.name)
elif edit=='Time zone':
  print('Please go to https://launchpad.net/~%s/+editlocation to do so'% me.name)
else:
  print('Sorry ! This is not writeable according to Launchpad API')
