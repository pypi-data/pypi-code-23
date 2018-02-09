import sys, tempfile, os, shutil
from subprocess import call

# Loosely based on StackOverflow: call up an EDITOR (vim) from a python script
EDITOR = os.environ.get('EDITOR','vi')

def edit_text(text=None):
    # Edit block of text in a single string, returning the edited result
    tf = tempfile.NamedTemporaryFile(suffix=".tmp")
    if text:
        tf.write(text)
        tf.flush()
    call([EDITOR, tf.name])
    with open(tf.name, 'r') as newfile:
        text = newfile.read()
    tf.close()
    try:
        # Attempt to clean hidden temp files that EDITOR may have created
        os.remove(tf.name + "~")
    except OSError:
        pass
    return text

def edit_file(name, backup=None):
    # Edit file in place, optionally backing up first
    # Returns True if file was modified else False
    if backup:
        shutil.copy2(name, backup)
    # Record time of last modification: tolm
    previous_tolm = os.stat(name).st_mtime
    call([EDITOR, name])
    current_tolm  = os.stat(name).st_mtime
    return current_tolm != previous_tolm
