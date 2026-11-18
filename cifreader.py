# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
A reader for Crystallographic Information Files (CIF), the IUCr's open standard, in Python
only.

It follows the CIF 1.1 syntax (https://www.iucr.org/resources/cif/spec/version1.1/cifsyntax):

- a file holds data blocks, each started by ``data_<name>``;
- a data item is a data name (a tag starting with ``_``, case-insensitive) and its value;
- ``loop_`` starts a table: its data names, then their values, row by row;
- values are unquoted (ending at whitespace), quoted with ``'`` or ``"`` (a closing quote
  must be followed by whitespace or the end of the line), or text fields between lines that
  start with ``;``;
- ``#`` starts a comment, outside values; ``data_``, ``loop_``, ``save_``, ``global_`` and
  ``stop_`` are reserved words; save frames (dictionaries) and global blocks are skipped.

Files that start with the CIF 2.0 code (``#\\#CIF_2.0``) follow CIF 2.0 (Bernstein et al.,
J. Appl. Cryst. 49 (2016) 277-284), which changes or adds:

- a single- or double-quoted value ends at the next matching quote, on the same line;
- triple-quoted values (between three single or three double quotes), which may span lines;
- lists, ``[value value ...]``, and tables, ``{"key":value ...}`` (quoted keys, each followed
  directly by ``:``), whose values may be lists and tables in turn, over several lines;
- ``[``, ``]``, ``{`` and ``}`` can't appear in unquoted values: they end them.

Values are returned as strings, as written (without their delimiters): ``?`` and ``.`` are
the strings ``'?'`` and ``'.'``. Looped values are lists of strings. A CIF 2.0 list is a
:py:class:`CifList` (a tuple) and a table a :py:class:`CifTable` (a dict), so they're never
mistaken for looped values.

:py:func:`~pyemaps.fileutils.loadCrystalCIFData` uses this module, through
:py:meth:`Crystal.from_cif <pyemaps.crystals.Crystal.from_cif>`.
'''
import os

RESERVED = ('data_', 'loop_', 'save_', 'global_', 'stop_')
CIF2_MAGIC = '#\\#CIF_2.0'


class CifSyntaxError(ValueError):
    '''A file that doesn't follow the CIF syntax, with the line number and the reason.'''


class CifList(tuple):
    '''A CIF 2.0 list value: its values, which are strings, lists or tables.'''


class CifTable(dict):
    '''A CIF 2.0 table value: its values by key; values are strings, lists or tables.'''


class CifBlock:
    '''
    One data block: its data items by name. Names are case-insensitive. A value is a string,
    or a list of strings for a looped data name.
    '''

    def __init__(self, name):
        self.name = name
        self._items = {}
        self._names = []                       # data names as written, in order
        self.loops = []                        # each loop's data names, lower case

    def __contains__(self, tag):
        return tag.lower() in self._items

    def __getitem__(self, tag):
        return self._items[tag.lower()]

    def get(self, tag, default=None):
        return self._items.get(tag.lower(), default)

    def keys(self):
        return list(self._names)

    def __len__(self):
        return len(self._items)

    def _set(self, tag, value, where):
        key = tag.lower()
        if key in self._items:
            raise CifSyntaxError(f'{where}: data name {tag} appears twice in data block '
                                 f'{self.name}')
        self._items[key] = value
        self._names.append(tag)

    def __repr__(self):
        return f'CifBlock({self.name!r}: {len(self._items)} data names)'


def read_cif(path):
    '''
    Read a CIF file.

    :param path: the file.
    :type path: str or os.PathLike
    :return: the data blocks, in file order.
    :rtype: list of CifBlock
    :raise OSError: if the file can't be read.
    :raise CifSyntaxError: if the file doesn't follow the CIF syntax.
    '''
    path = os.fspath(path)
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'latin-1'):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return parse_cif(text, path)


def parse_cif(text, source='<string>'):
    '''Parse CIF text into its data blocks; see :py:func:`read_cif`.'''
    tokens = _tokens(text, source)
    return _blocks(tokens, source)


# ------------------------------------------------------------------ tokens

TAG, VALUE, WORD = 'tag', 'value', 'word'          # WORD: a reserved word
KEY = 'key'                                         # a CIF 2.0 table key, with its ":"
OPENERS = {'[': ']', '{': '}'}


def _tokens(text, source):
    '''(kind, text, line number) for every token, comments and whitespace removed.'''
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if text.startswith(CIF2_MAGIC):
        return _tokens_cif2(text, source)
    lines = text.split('\n')
    out = []
    n = 0
    while n < len(lines):
        line = lines[n]
        if line.startswith(';'):                   # a text field, to the next ";" line
            start = n
            body = [line[1:]]
            n += 1
            while n < len(lines) and not lines[n].startswith(';'):
                body.append(lines[n])
                n += 1
            if n == len(lines):
                raise CifSyntaxError(f'{source}, line {start + 1}: a text field (";") is '
                                     'never closed')
            out.append((VALUE, '\n'.join(body), start + 1))
            rest = lines[n][1:]
            n += 1
            _line_tokens(rest, n, source, out)
            continue
        _line_tokens(line, n + 1, source, out)
        n += 1
    return out


def _line_tokens(line, lineno, source, out):
    '''CIF 1.1 tokens on one line.'''
    i, size = 0, len(line)
    while i < size:
        c = line[i]
        if c in ' \t':
            i += 1
            continue
        if c == '#':
            return
        if c in '\'"':
            j = i + 1
            while True:
                j = line.find(c, j)
                if j < 0:
                    raise CifSyntaxError(f'{source}, line {lineno}: a quoted value ({c}) is '
                                         'never closed on its line')
                if j + 1 == size or line[j + 1] in ' \t':    # CIF 1.1: quote + space ends it
                    break
                j += 1
            out.append((VALUE, line[i + 1:j], lineno))
            i = j + 1
            continue
        j = i
        while j < size and line[j] not in ' \t':
            j += 1
        word = line[i:j]
        low = word.lower()
        if c == '_':
            out.append((TAG, word, lineno))
        elif low.startswith(RESERVED):
            out.append((WORD, word, lineno))
        else:
            out.append((VALUE, word, lineno))
        i = j


def _tokens_cif2(text, source):
    '''CIF 2.0 tokens, from a character stream: lists, tables and quoted values may span lines.'''
    out = []
    i, size, line = 0, len(text), 1
    at_line_start = True
    while i < size:
        c = text[i]
        if c == '\n':
            line += 1
            i += 1
            at_line_start = True
            continue
        if c in ' \t':
            i += 1
            at_line_start = False
            continue
        if c == ';' and at_line_start:                     # a text field
            end = text.find('\n;', i)
            if end < 0:
                raise CifSyntaxError(f'{source}, line {line}: a text field (";") is never closed')
            out.append((VALUE, text[i + 1:end], line))
            line += text.count('\n', i, end + 1)
            i = end + 2
            at_line_start = False
            continue
        at_line_start = False
        if c == '#':
            j = text.find('\n', i)
            i = size if j < 0 else j
            continue
        if text.startswith(("'''", '"""'), i):
            q = text[i:i + 3]
            end = text.find(q, i + 3)
            if end < 0:
                raise CifSyntaxError(f'{source}, line {line}: a triple-quoted value is never closed')
            value, start_line = text[i + 3:end], line
            line += text.count('\n', i, end)
            i = end + 3
            i = _string_token(text, i, value, start_line, out)
            continue
        if c in '\'"':
            end = text.find(c, i + 1)
            nl_at = text.find('\n', i + 1)
            if end < 0 or (0 <= nl_at < end):
                raise CifSyntaxError(f'{source}, line {line}: a quoted value ({c}) is never closed '
                                     'on its line')
            i = _string_token(text, end + 1, text[i + 1:end], line, out)
            continue
        if c in '[]{}':
            out.append((c, c, line))
            i += 1
            continue
        j = i
        while j < size and text[j] not in ' \t\n[]{}':
            j += 1
        word = text[i:j]
        if c == '_':
            out.append((TAG, word, line))
        elif word.lower().startswith(RESERVED):
            out.append((WORD, word, line))
        else:
            out.append((VALUE, word, line))
        i = j
    return out


def _string_token(text, i, value, line, out):
    '''A quoted value, or a table key when ":" follows it directly. Returns the next position.'''
    if i < len(text) and text[i] == ':':
        out.append((KEY, value, line))
        return i + 1
    out.append((VALUE, value, line))
    return i


# ------------------------------------------------------------------ blocks

def _blocks(tokens, source):
    blocks = []
    block = None
    k, size = 0, len(tokens)
    while k < size:
        kind, word, line = tokens[k]
        where = f'{source}, line {line}'
        low = word.lower()
        if kind == WORD and low.startswith('data_'):
            name = word[5:]
            if not name:
                raise CifSyntaxError(f'{where}: a data block without a name')
            block = CifBlock(name)
            blocks.append(block)
            k += 1
        elif kind == WORD and (low.startswith('save_') or low == 'global_'):
            k = _skip_frame(tokens, k, source)
        elif block is None:
            raise CifSyntaxError(f'{where}: {word!r} comes before the first data block '
                                 '("data_...")')
        elif kind == WORD and low == 'loop_':
            k = _loop(tokens, k + 1, block, source)
        elif kind == TAG:
            if k + 1 >= size or tokens[k + 1][0] not in (VALUE, '[', '{'):
                raise CifSyntaxError(f'{where}: data name {word} has no value')
            value, k = _value(tokens, k + 1, source)
            block._set(word, value, where)
        elif kind == WORD and low == 'stop_':
            k += 1
        elif kind in (']', '}'):
            raise CifSyntaxError(f'{where}: "{kind}" closes a list or table that never started')
        elif kind == KEY:
            raise CifSyntaxError(f'{where}: table key {word!r} outside a table')
        else:
            raise CifSyntaxError(f'{where}: value {word!r} has no data name')
    return blocks


def _value(tokens, k, source):
    '''One value from token k: a string, or a CIF 2.0 list or table. Returns (value, next k).'''
    kind, word, line = tokens[k]
    if kind == VALUE:
        return word, k + 1
    if kind not in OPENERS:
        raise CifSyntaxError(f'{source}, line {line}: expected a value, not {word!r}')
    close = OPENERS[kind]
    items = [] if kind == '[' else {}
    k += 1
    while True:
        if k >= len(tokens):
            raise CifSyntaxError(f'{source}, line {line}: a {"list" if kind == "[" else "table"} '
                                 f'("{kind}") is never closed')
        t, w, l = tokens[k]
        if t == close:
            k += 1
            break
        if kind == '[':
            if t == KEY:
                raise CifSyntaxError(f'{source}, line {l}: table key {w!r} in a list')
            v, k = _value(tokens, k, source)
            items.append(v)
        else:
            if t != KEY:
                raise CifSyntaxError(f'{source}, line {l}: a table entry must be a quoted key '
                                     f'followed directly by ":", not {w!r}')
            if k + 1 >= len(tokens) or tokens[k + 1][0] in (']', '}', KEY):
                raise CifSyntaxError(f'{source}, line {l}: table key {w!r} has no value')
            v, k = _value(tokens, k + 1, source)
            items[w] = v
    return (CifList(items) if kind == '[' else CifTable(items)), k


def _loop(tokens, k, block, source):
    size = len(tokens)
    names = []
    while k < size and tokens[k][0] == TAG:
        names.append(tokens[k][1])
        k += 1
    line = tokens[k - 1][2] if k else 0
    if not names:
        raise CifSyntaxError(f'{source}, line {line}: loop_ without data names')
    values = []
    while k < size and tokens[k][0] in (VALUE, '[', '{'):
        value, k = _value(tokens, k, source)
        values.append(value)
    if not values or len(values) % len(names):
        raise CifSyntaxError(f'{source}, line {line}: a loop of {len(names)} data names has '
                             f'{len(values)} values, not a whole number of rows')
    where = f'{source}, line {line}'
    for c, name in enumerate(names):
        block._set(name, values[c::len(names)], where)
    block.loops.append([n.lower() for n in names])
    return k


def _skip_frame(tokens, k, source):
    '''Skip a save frame (save_name ... save_) or a global_ block.'''
    _, word, line = tokens[k]
    if word.lower() == 'global_':
        k += 1
        while k < len(tokens) and not (tokens[k][0] == WORD and
                                       tokens[k][1].lower().startswith('data_')):
            k += 1
        return k
    if word.lower() == 'save_':
        raise CifSyntaxError(f'{source}, line {line}: "save_" ends a save frame that never '
                             'started')
    k += 1
    while k < len(tokens):
        if tokens[k][0] == WORD and tokens[k][1].lower() == 'save_':
            return k + 1
        k += 1
    raise CifSyntaxError(f'{source}, line {line}: save frame {word[5:]} is never closed')
