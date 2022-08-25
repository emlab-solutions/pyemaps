# To maximize python3/python2 compatibility
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

#
# helper code: we define our match tokens
lastval = ''
def monitor(location,value):
    global lastval
    #print 'At %s: %s' % (location,repr(value))
    lastval = repr(value)
    return value


# Begin -- grammar generated by Yapps
import sys, re
from . import yapps3_compiled_rt as yappsrt

class TypeParserScanner(yappsrt.Scanner):
    def __init__(self, *args,**kwargs):
        patterns = [
         ('([ \t\n\r])', '([ \t\n\r])'),
         ('container', '[A-Za-z]+\\('),
         ('identifier', '[A-Za-z]+'),
         ('c_c_b', '\\)'),
         ('o_c_b', '\\('),
         ('comma', '\\,'),
         ('END', '$'),
        ]
        yappsrt.Scanner.__init__(self,patterns,['([ \t\n\r])'],*args,**kwargs)

class TypeParser(yappsrt.Parser):
    Context = yappsrt.Context
    def input(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'input', [])
        base_element = self.base_element(_context)
        p = [base_element]
        while self._peek('END', 'comma') == 'comma':
            comma = self._scan('comma')
            base_element = self.base_element(_context)
            p.append(base_element)
        if self._peek() not in ['END', 'comma']:
            raise yappsrt.YappsSyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['comma', 'END']))
        END = self._scan('END')
        if len(p)==1: p = p[0]
        return p

    def base_element(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'base_element', [])
        _token = self._peek('container', 'identifier')
        if _token == 'container':
            container = self._scan('container')
            element_list = self.element_list(_context)
            c_c_b = self._scan('c_c_b')
            return element_list
        else: # == 'identifier'
            identifier = self._scan('identifier')
        return identifier

    def element_list(self, _parent=None):
        _context = self.Context(_parent, self._scanner, self._pos, 'element_list', [])
        base_element = self.base_element(_context)
        p = [base_element]
        while self._peek('comma', 'c_c_b') == 'comma':
            comma = self._scan('comma')
            base_element = self.base_element(_context)
            p.append(base_element)
        if self._peek() not in ['comma', 'c_c_b']:
            raise yappsrt.YappsSyntaxError(charpos=self._scanner.get_prev_char_pos(), context=_context, msg='Need one of ' + ', '.join(['comma', 'c_c_b']))
        return p


def parse(rule, text):
    P = TypeParser(TypeParserScanner(text))
    return yappsrt.wrap_error_reporter(P, rule)

# End -- grammar generated by Yapps



