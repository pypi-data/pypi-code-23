from collections import Iterable
from io import StringIO
import sys
from regex import compile

string = """

Stack Overflow

    Questions
    Developer Jobs
    Tags
    Users

Running unittest with typical test directory structure
Ask Question
up vote
431
down vote
favorite
153
	

The very common directory structure for even a simple Python module seems to be to separate the unit tests into their own test directory:

new_project/
    antigravity/
        antigravity.py
    test/
        test_antigravity.py
    setup.py
    etc.

for example see this Python project howto.

My question is simply What's the usual way of actually running the tests? I suspect this is obvious to everyone except me, but you can't just run python test_antigravity.py from the test directory as its import antigravity will fail as the module is not on the path.

I know I could modify PYTHONPATH and other search path related tricks, but I can't believe that's the simplest way - it's fine if you're the developer but not realistic to expect your users to use if they just want to check the tests are passing.

The other alternative is just to copy the test file into the other directory, but it seems a bit dumb and misses the point of having them in a separate directory to start with.

So, if you had just downloaded the source to my new project how would you run the unit tests? I'd prefer an answer that would let me say to my users: "To run the unit tests do X."
python unit-testing
shareeditflag
	
edited Sep 29 '10 at 23:18
Scott Griffiths
14.9k54070
	
asked Dec 13 '09 at 16:10
Major Major
2,3183139
	
83 	
  	
	
Same here. I can't believe that there is no proper solution (not involving hacking the path) to this fundamental and very common problem. Python designers: FAIL! – EMP Apr 22 '10 at 1:52
4 	
  	
	
@EMP The proper solution when you need to set the search path is to... set the search path. What sort of solution were you expecting? – Carl Meyer Feb 17 '12 at 20:12
3 	
  	
	
@CarlMeyer another better solution is to use the unittest command line interface as described in my answer below so you don't have to add the directory to the path. – Pierre Jun 27 '14 at 18:30
5 	
  	
	
Same here. I just embarked on writing my very first unit tests in for a tiny Python project and took several days trying to reason with the fact that I can't readily run a test while keeping my sources in a src directory and tests in a test directory, seemingly with any of the existing test frameworks. I'll eventually accept things, figure out a way; but this has been a very frustrating introduction. (And I'm a unit testing veteran outside Python.) – Ates Goral Mar 30 '16 at 20:43
	
add a comment
	
start a bounty
14 Answers
active
oldest
votes
up vote
388
down vote
accepted
	

The best solution in my opinion is to use the unittest command line interface which will add the directory to the sys.path so you don't have to (done in the TestLoader class).

For example for a directory structure like this:

new_project
├── antigravity.py
└── test_antigravity.py

You can just run:

$ cd new_project
$ python -m unittest test_antigravity

For a directory structure like yours:

new_project
├── antigravity
│   ├── __init__.py         # make it a package
│   └── antigravity.py
└── test
    ├── __init__.py         # also make test a package
    └── test_antigravity.py

And in the test modules inside the test package, you can import the antigravity package and its modules as usual:

# import the package
import antigravity

# import the antigravity module
from antigravity import antigravity

# or an object inside the antigravity module
from antigravity.antigravity import my_object

Running a single test module:

To run a single test module, in this case test_antigravity.py:

$ cd new_project
$ python -m unittest test.test_antigravity

Just reference the test module the same way you import it.

Running a single test case or test method:

Also you can run a single TestCase or a single test method:

$ python -m unittest test.test_antigravity.GravityTestCase
$ python -m unittest test.test_antigravity.GravityTestCase.test_method

Running all tests:

You can also use test discovery which will discover and run all the tests for you, they must be modules or packages named test*.py (can be changed with the -p, --pattern flag):

$ cd new_project
$ python -m unittest discover

This will run all the test*.py modules inside the test package.
shareeditflag
	
edited Nov 23 '14 at 8:49
	
answered Jun 17 '14 at 14:49
Pierre
5,10422346
	
9 	
  	
	
python -m unittest discover will find and run tests in the test directory if they are named test*.py. If you named the subdirectory tests, use python -m unittest discover -s tests, and if you named the test files antigravity_test.py, use python -m unittest discover -s tests -p '*test.py' File names can use underscores but not dashes. – Mike3d0g May 18 '15 at 2:49
   	
  	
	
I am new to python. Can you give an example of what antigravity.py would contain, given the directory structure that resembles the second example. I can imagine my question is really what is the difference between package and module, but would like insight into their distinction within the context of this scenario. Thank you! – walkerrandophsmith Oct 1 '15 at 19:03
   	
  	
	
Note that with this solution you cannot use explicit paths in test_antigravity.py e.g. import .antigravity will not work it must be import antigravity – Alexander McFarlane Jun 15 '16 at 4:08
2 	
  	
	
This fails for me on Python 3 with the error ImportError: No module named 'test.test_antigravity' because of a conflict with the test sub-module of the unittest library. Maybe an expert can confirm and change the answer sub-directory name to e.g., 'tests' (plural). – expz Dec 22 '16 at 21:45
3 	
  	
	
My test_antigravity.py still throws an import error for both import antigravity and from antigravity import antigravity, as well. I have both __init_.py files and I am calling python3 -m unittest discover from the new project directory. What else could be wrong? – Drunken Master May 2 '17 at 20:11
	
add a comment |  show 3 more comments
up vote
42
down vote
	

The simplest solution for your users is to provide an executable script (runtests.py or some such) which bootstraps the necessary test environment, including, if needed, adding your root project directory to sys.path temporarily. This doesn't require users to set environment variables, something like this works fine in a bootstrap script:

import sys, os

sys.path.insert(0, os.path.dirname(__file__))

Then your instructions to your users can be as simple as "python runtests.py".

Of course, if the path you need really is os.path.dirname(__file__), then you don't need to add it to sys.path at all; Python always puts the directory of the currently running script at the beginning of sys.path, so depending on your directory structure, just locating your runtests.py at the right place might be all that's needed.

Also, the unittest module in Python 2.7+ (which is backported as unittest2 for Python 2.6 and earlier) now has test discovery built-in, so nose is no longer necessary if you want automated test discovery: your user instructions can be as simple as "python -m unittest discover".
shareeditflag
	
edited Feb 23 '12 at 5:15
	
answered Dec 13 '09 at 20:40
Carl Meyer
52.1k1593105
	
   	
  	
	
I put some tests in a subfolder like as "Major Major". They can run with python -m unittest discover but how can I select to run only one of them. If I run python -m unittest tests/testxxxxx then it fails for path issue. Since dicovery mode solve everything I would expect that there is another trick to solve path issue without handcoding path fix you suggest in first point – Frederic Bazin May 23 '12 at 16:07
1 	
  	
	
@FredericBazin Don't use discovery if you only want a single test or test file, just name the module you want to run. If you name it as a module dotted-path (rather than a file path) it can figure out the search path correctly. See Peter's answer for more details. – Carl Meyer Jul 15 '14 at 1:01
	
add a comment
up vote
16
down vote
	

I generally create a "run tests" script in the project directory (the one that is common to both the source directory and test) that loads my "All Tests" suite. This is usually boilerplate code, so I can reuse it from project to project.

run_tests.py:

import unittest
import test.all_tests
testSuite = test.all_tests.create_test_suite()
text_runner = unittest.TextTestRunner().run(testSuite)

test/all_tests.py (from How do I run all Python unit tests in a directory?)

import glob
import unittest

def create_test_suite():
    test_file_strings = glob.glob('test/test_*.py')
    module_strings = ['test.'+str[5:len(str)-3] for str in test_file_strings]
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) \
              for name in module_strings]
    testSuite = unittest.TestSuite(suites)
    return testSuite

With this setup, you can indeed just include antigravity in your test modules. The downside is you would need more support code to execute a particular test... I just run them all every time.
shareeditflag
	
edited May 23 '17 at 12:03
Community♦
11
	
answered Jun 7 '10 at 19:30
stw_dev
637814
	
add a comment
up vote
16
down vote
	

From the article you linked to:

    Create a test_modulename.py file and put your unittest tests in it. Since the test modules are in a separate directory from your code, you may need to add your module’s parent directory to your PYTHONPATH in order to run them:

    $ cd /path/to/googlemaps

    $ export PYTHONPATH=$PYTHONPATH:/path/to/googlemaps/googlemaps

    $ python test/test_googlemaps.py

    Finally, there is one more popular unit testing framework for Python (it’s that important!), nose. nose helps simplify and extend the builtin unittest framework (it can, for example, automagically find your test code and setup your PYTHONPATH for you), but it is not included with the standard Python distribution.

Perhaps you should look at nose as it suggests?
shareeditflag
	
answered Dec 13 '09 at 16:25
Mark Byers
527k11112501288
	
2 	
  	
	
+1 for nose. It works very well. – Virgil Dupras Dec 13 '09 at 16:32
3 	
  	
	
Yes this works (for me), but I'm really asking for the simplest instructions that I can give users to my module to get them to run the tests. Modifying the path might actually be it, but I'm fishing for something more straight-forward. – Major Major Dec 13 '09 at 16:39
2 	
  	
	
So what does your python path look like after you've worked on a hundred projects? Am I supposed to manually go in and clean up my path? If so this is an odious design! – jeremyjjbrown Jun 21 '14 at 23:16
   	
  	
	
nose link is broken – TinyTheBrontosaurus Nov 1 '17 at 13:28
	
add a comment
up vote
5
down vote
	

if you run "python setup.py develop" then the package will be in the path. But you may not want to do that because you could infect your system python installation, which is why tools like virtualenv and buildout exist.
shareeditflag
	
answered Dec 13 '09 at 16:27
Tom Willis
4,3841631
	
add a comment
up vote
4
down vote
	

Use setup.py develop to make your working directory be part of the installed Python environment, then run the tests.
shareeditflag
	
answered Dec 13 '09 at 16:24
Ned Batchelder
226k42400545
	
   	
  	
	
This gets me an invalid command 'develop' and this option isn't mentioned if I ask for setup.py --help-commands. Does there need to be something in the setup.py itself for this to work? – Major Major Dec 13 '09 at 16:43
   	
  	
	
It's OK - the problem was I was missing an import setuptools from my setup.py file. But I guess that does go to show that this won't work all the time for other people's modules. – Major Major Dec 13 '09 at 16:54
1 	up voted
  	
	
If you have pip, you can use that to install your package in "editable" mode: pip install -e . This likewise adds the package to the Python environment without copying the source, allowing you to continue to edit it where it lies. – Eric Smith Feb 4 '14 at 23:39
   	
  	
	
pip install -e . is the exact same thing as python setup.py develop, it just monkeypatches your setup.py to use setuptools even if it doesn't actually, so it works either way. – Carl Meyer Jul 15 '14 at 0:57
	
add a comment
up vote
4
down vote
	

I had the same problem, with a separate unit tests folder. From the mentioned suggestions I add the absolute source path to sys.path.

The benefit of the following solution is, that one can run the file test/test_yourmodule.py without changing at first into the test-directory:

import sys, os
testdir = os.path.dirname(__file__)
srcdir = '../src/projekt/dir'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))

import yourmodule
import unittest

shareeditflag
	
answered Dec 4 '13 at 9:45
andpei
1,55011231
	
add a comment
up vote
3
down vote
	

If you use VS Code and your tests are located on the same level as your project then running and debug your code doesn't work out of the box. What you can do is change your launch.json file:

{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python",
            "type": "python",
            "request": "launch",
            "stopOnEntry": false,
            "pythonPath": "${config:python.pythonPath}",
            "program": "${file}",
            "cwd": "${workspaceRoot}",
            "env": {},
            "envFile": "${workspaceRoot}/.env",
            "debugOptions": [
                "WaitOnAbnormalExit",
                "WaitOnNormalExit",
                "RedirectOutput"
            ]
        }    
    ]
}

The key line here is envFile

"envFile": "${workspaceRoot}/.env",

In the root of your project add .env file

Inside of your .env file add path to the root of your project. This will temporarily add

    PYTHONPATH=C:\YOUR\PYTHON\PROJECT\ROOT_DIRECTORY

path to your project and you will be able to use debug unit tests from VS Code
shareeditflag
	
edited May 28 '17 at 0:38
	
answered May 27 '17 at 23:45
Vlad Bezden
19.2k79997
	
add a comment
up vote
2
down vote
	

Following is my project structure:

ProjectFolder:
 - project:
     - __init__.py
     - item.py
 - tests:
     - test_item.py

I found it better to import in the setUp() method:

import unittest
import sys    

class ItemTest(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, "../project")
        from project import item
        # further setup using this import

    def test_item_props(self):
        # do my assertions

if __name__ == "__main__":
    unittest.main()

shareeditflag
	
answered Jul 25 '17 at 14:01
rolika
29019
	
add a comment
up vote
2
down vote
	

    What's the usual way of actually running the tests

I use Python 3.6.2

cd new_project

pytest test/test_antigravity.py

To install pytest: sudo pip install pytest

I didn't set any path variable and my imports are not failing with the same "test" project structure.

I commented out this stuff: if __name__ == '__main__' like this:

test_antigravity.py

import antigravity

class TestAntigravity(unittest.TestCase):

    def test_something(self):

        # ... test stuff here


# if __name__ == '__main__':
# 
#     if __package__ is None:
# 
#         import something
#         sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
#         from .. import antigravity
# 
#     else:
# 
#         from .. import antigravity
# 
#     unittest.main()

shareeditflag
	
edited Jul 26 '17 at 21:55
	
answered Jul 26 '17 at 21:43
aliopi
1,77611618
	
add a comment
up vote
2
down vote
	

Solution/Example for Python unittest module

Given the following project structure:

ProjectName
 ├── project_name
 |    ├── models
 |    |    └── thing_1.py
 |    └── __main__.py
 └── test
      ├── models
      |    └── test_thing_1.py
      └── __main__.py

You can run your project from the root directory with python project_name, which calls ProjectName/project_name/__main__.py.

To run your tests with python test, effectively running ProjectName/test/__main__.py, you need to do the following:

1) Turn your test/models directory into a package by adding a __init__.py file. This makes the test cases within the sub directory accessible from the parent test directory.

# ProjectName/test/models/__init__.py

from .test_thing_1 import Thing1TestCase        

2) Modify your system path in test/__main__.py to include the project_name directory.

# ProjectName/test/__main__.py

import sys
import unittest

sys.path.append('../project_name')

loader = unittest.TestLoader()
testSuite = loader.discover('test')
testRunner = unittest.TextTestRunner(verbosity=2)
testRunner.run(testSuite)

Now you can successfully import things from project_name in your tests.

# ProjectName/test/models/test_thing_1.py    

import unittest
from project_name.models import Thing1  # this doesn't work without 'sys.path.append' per step 2 above

class Thing1TestCase(unittest.TestCase):

    def test_thing_1_init(self):
        thing_id = 'ABC'
        thing1 = Thing1(thing_id)
        self.assertEqual(thing_id, thing.id)

shareeditflag
	
answered Jun 28 '17 at 23:45
Derek Soike
2,3381930
	
add a comment
up vote
2
down vote
	

It's possible to use wrapper which runs selected or all tests.

For instance:

./run_tests antigravity/*.py

or to run all tests recursively use globbing (tests/**/*.py) (enable by shopt -s globstar).

The wrapper can basically use argparse to parse the arguments like:

parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='*')

Then load all the tests:

for filename in args.files:
    exec(open(filename).read())

then add them into your test suite (using inspect):

alltests = unittest.TestSuite()
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj) and name.startswith("FooTest"):
        alltests.addTest(unittest.makeSuite(obj))

and run them:

result = unittest.TextTestRunner(verbosity=2).run(alltests)

Check this example for more details.

See also: How to run all Python unit tests in a directory?
shareeditflag
	
edited Nov 30 '17 at 13:13
	
answered Jun 7 '15 at 11:45
kenorb
45.5k17288295
	
add a comment
up vote
1
down vote
	

I noticed that if you run the unittest command line interface from your "src" directory, then imports work correctly without modification.

python -m unittest discover -s ../test

If you want to put that in a batch file in your project directory, you can do this:

setlocal & cd src & python -m unittest discover -s ../test

shareeditflag
	
answered Aug 7 '17 at 23:13
Alan Lynn
318313
	
add a comment
up vote
-3
down vote
	

You should really use the pip tool.

Use pip install -e to install your package in development mode. This is a very good practise.

In the Ref url given below, 2 classic project (with test) layout are given, you can follow any of them.

Ref:

    1 https://pytest.org/latest/goodpractices.html#goodpractices

shareeditflag
	
edited May 23 '17 at 11:54
Community♦
11
	
answered Mar 7 '14 at 7:51
squid
1,5431616
	
   	
  	
	
Why downvote this answer? I read the accepted answer and while it was not bad, pytest is way better to run tests, because of the console output you get, in color, with stack trace info and detailed assertion error information. – aliopi Jul 26 '17 at 21:38
	
add a comment
Your Answer

 
community wiki
Not the answer you're looking for? Browse other questions tagged python unit-testing or ask your own question.

asked
	

8 years, 1 month ago

viewed
	

92,454 times

active
	

1 month ago
Featured on Meta
What criteria should we use to determine which review queue indicator a site…

Hot Meta Posts
11
Reviewing in help center

5
Automatic syntax highlighting for Spark Python & R APIs (PySpark & SparkR)

17
Can I ask a question about code in a GitHub repository which is no longer…

3
Repeated “Sign up” options

94 People Chatting
PHP
36 mins ago - Sjon
[Sjon: 36 mins ago] [Linus: 39 mins ago] [Leigh: 50 mins ago] [Akshay: 52 mins ago] [Joe Watkins: 1 hour ago] [SaitamaSama: 1 hour ago] [Naruto: 1 hour ago]
JavaScript
49 mins ago - Tavo
[Tavo: 49 mins ago] [Neil: 50 mins ago] [Kamil Solecki: 51 mins ago] [Marek: 1 hour ago] [Basheer Ahmed Kharoti: 1 hour ago] [KarelG: 1 hour ago] [Caprica Six: 3 hours ago]
Linked
158
How do I run all Python unit tests in a directory?
19
Python import src modules when running tests
14
How to make my Python unit tests to import the tested modules if they are in sister folders?
2
How to import the src from the tests module in python
2
Bootstrapping tests and using Python test discovery
9
What's the normal structure of a Python open source project and what's the preferred way of running the tests?
1
Python unittest failing to resolve import statements
3
Python project structure and relative imports
1
How do you create a python package with a built in “test/main.py” main function?
4
Trivial python import fails
see more linked questions…
Related
2128
How do I test a private function or a class that has private methods, fields or inner classes?
1710
Is there a way to run Python on Android?
2578
How can I create a directory if it does not exist?
158
How do I run all Python unit tests in a directory?
2398
How do I list all files of a directory?
694
Peak detection in a 2D array
1265
Find current directory and file's directory
56
Python package structure, setup.py for running unit tests
124
Testing service in Angular returns module is not defined
16
How to make python unit tests always find test data files when run from different working directories?
Hot Network Questions

    Could a plant grow on a building taller than mount Everest?
    How do you find helpers for larger DIY projects?
    Can a spell always counterspell itself?
    How do I model this curvy spiral staircase?
    Function pointers in C - nature and usage
    Why would Putin even bother barring Navalny from participating?
    Can we destroy an asteroid by spinning it?
    Latex3 Token-List commands do not work as expected
    Different Print Page Dimensions Under Same Standard (A4)?
    Code I get from wolfram isn't working in mathematica
    It seems as though my employer wants me to come into work when I'm ill. Am I missing something?
    Why are chip designers called "triangle pushers"?
    Finding the 10th root of a matrix
    Using "If" statement to change a list values
    Is there any way to score an automatic natural 20?
    How to invite terminal ill / very sick friends to a party?
    Mathematicians' Tensors vs. Physicists' Tensors
    You'll never walk out of this room
    Postdoc overwhelmed with all incomplete work
    How do I politely tell my coworker he can do the work himself?
    Why can't a Tercio use crossbows and pikes?
    What happened to the humans in "Cars" (that is if they ever existed)?
    How to 'fix' this in an enclosure without glueing?
    FreeBSD: Directory called ^C (really!) - how to remove?

question feed
Stack Overflow

    Questions
    Jobs
    Developer Jobs Directory
    Salary Calculator
    Help
    Mobile

Stack Overflow Business

    Talent
    Ads
    Enterprise

Company

    About
    Press
    Work Here
    Legal
    Privacy Policy
    Contact Us

Stack Exchange Network

    Technology
    Life / Arts
    Culture / Recreation
    Science
    Other

    Stack Overflow
    Server Fault
    Super User
    Web Applications
    Ask Ubuntu
    Webmasters
    Game Development

    TeX - LaTeX
    Software Engineering
    Unix & Linux
    Ask Different (Apple)
    WordPress Development
    Geographic Information Systems
    Electrical Engineering

    Android Enthusiasts
    Information Security
    Database Administrators
    Drupal Answers
    SharePoint
    User Experience
    Mathematica

    Salesforce
    ExpressionEngine® Answers
    Stack Overflow em Português
    Blender
    Network Engineering
    Cryptography
    Code Review

    Magento
    Software Recommendations
    Signal Processing
    Emacs
    Raspberry Pi
    Stack Overflow на русском
    Programming Puzzles & Code Golf

    Stack Overflow en español
    Ethereum
    Data Science
    Arduino
    Bitcoin
    more (26)

    Photography
    Science Fiction & Fantasy
    Graphic Design
    Movies & TV
    Music: Practice & Theory
    Worldbuilding
    Seasoned Advice (cooking)

    Home Improvement
    Personal Finance & Money
    Academia
    Law
    more (16)

    English Language & Usage
    Skeptics
    Mi Yodeya (Judaism)
    Travel
    Christianity
    English Language Learners
    Japanese Language

    Arqade (gaming)
    Bicycles
    Role-playing Games
    Anime & Manga
    Puzzling
    Motor Vehicle Maintenance & Repair
    more (32)

    MathOverflow
    Mathematics
    Cross Validated (stats)
    Theoretical Computer Science
    Physics
    Chemistry
    Biology

    Computer Science
    Philosophy
    more (10)

    Meta Stack Exchange
    Stack Apps
    API
    Data
    Area 51

    Blog Facebook Twitter LinkedIn 

site design / logo © 2018 Stack Exchange Inc; user contributions licensed under cc by-sa 3.0 with attribution required. rev 2018.1.30.28658
"""

from timeit import timeit

a = compile('(aaa|bbb|ccc|ddd|eee|fff|ggg|hhh|iii)').search
b = compile('(?:aaa|bbb|ccc|ddd|eee|fff|ggg|hhh|iii)').search
c = compile('(?>aaa|bbb|ccc|ddd|eee|fff|ggg|hhh|iii)').search
print(timeit('a(string)', globals=globals(), number=100))
print(timeit('b(string)', globals=globals(), number=100))
print(timeit('c(string)', globals=globals(), number=100))