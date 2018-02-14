"""{-
Copyright (c) 2009 Pauli Henrikki Rikula 

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
-}"""


class NotImplemented(Exception):
    pass


class Map:
    def __init__(self):
        pass
    
    def heuristic_estimate_of_distance(self, start,goal):
        """
        This should be >= 0
        If you want to be sure, that the found path is the sortest one,
        let this return a constant 0.
        """
        raise NotImplemented
    
    def neighbor_nodes(self, x):
        """
        x : the node of which neighbours you want to get 
        It might also be a good choise to implement a class for the node x
        """
        raise NotImplemented
    
    def dist_between(self, x, y):
        """
        The real distance between two adjacent nodes.
        This should be >= 0
        """

        raise NotImplemented
