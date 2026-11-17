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

Files that start with the CIF 2.0 code (``#\\#CIF_2.0``) are read too, with CIF 2.0's quoting
(a quote ends at the next matching quote) and triple-quoted strings; CIF 2.0 lists and tables
are refused.

Values are returned as strings, as written (without their delimiters): ``?`` and ``.`` are
the strings ``'?'`` and ``'.'``. Looped values are lists of strings.

:py:func:`~pyemaps.fileutils.loadCrystalCIFData` uses this module, through
:py:meth:`Crystal.from_cif <pyemaps.crystals.Crystal.from_cif>`.
'''
import os

RESERVED = ('data_', 'loop_', 'save_', 'global_', 'stop_')
CIF2_MAGIC = '#\\#CIF_2.0'


class CifSyntaxError(ValueError):
    '''A file that doesn't follow the CIF syntax, with the line number and the reason.'''


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


def _tokens(text, source):
    '''(kind, text, line number) for every token, comments and whitespace removed.'''
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    cif2 = lines[0].startswith(CIF2_MAGIC) if lines else False
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
            _line_tokens(rest, n, source, out, cif2)
            continue
        if cif2 and ("'''" in line or '"""' in line):
            n = _triple(lines, n, source, out)
            continue
        _line_tokens(line, n + 1, source, out, cif2)
        n += 1
    return out


def _line_tokens(line, lineno, source, out, cif2):
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
                if cif2 or j + 1 == size or line[j + 1] in ' \t':
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
        if cif2 and c in '[{':
            raise CifSyntaxError(f'{source}, line {lineno}: CIF 2.0 lists and tables aren\'t '
                                 'supported')
        if c == '_':
            out.append((TAG, word, lineno))
        elif low.startswith(RESERVED):
            out.append((WORD, word, lineno))
        else:
            out.append((VALUE, word, lineno))
        i = j


def _triple(lines, n, source, out):
    '''A CIF 2.0 line with a triple-quoted string, which may run over several lines.'''
    line = lines[n]
    for q in ("'''", '"""'):
        k = line.find(q)
        if k >= 0:
            break
    _line_tokens(line[:k], n + 1, source, out, True)
    start = n
    body, rest = line[k + 3:], None
    while True:
        e = body.find(q)
        if e >= 0:
            value, rest = body[:e], body[e + 3:]
            break
        n += 1
        if n == len(lines):
            raise CifSyntaxError(f'{source}, line {start + 1}: a triple-quoted value is never '
                                 'closed')
        body += '\n' + lines[n]
    out.append((VALUE, value, start + 1))
    _line_tokens(rest, n + 1, source, out, True)
    return n + 1


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
            if k + 1 >= size or tokens[k + 1][0] != VALUE:
                raise CifSyntaxError(f'{where}: data name {word} has no value')
            block._set(word, tokens[k + 1][1], where)
            k += 2
        elif kind == WORD and low == 'stop_':
            k += 1
        else:
            raise CifSyntaxError(f'{where}: value {word!r} has no data name')
    return blocks


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
    while k < size and tokens[k][0] == VALUE:
        values.append(tokens[k][1])
        k += 1
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
