'''
The MIT License

Copyright (c) 2010-2017 Josh A. Bosley, http://joshbosley.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

'''
    Default handler class meant to be used as an
    example for developing a handler class
'''

class handler:
    def __init__(self):
        print("Default handler is active ... ")

    def handle(self, data):
        print("Default handler has received : ", data)
        print("\tTo use a custom handler, pass a class containding a 'handle' function when")
        print("\tcreating the tcpServerInstance.")
        print("\n\tExample: tcpServerInstance('127.0.0.1', 9000, RequestHandlerClass)")
        return "[__DEFAULT__HANDLER__RESPONSE__]"
