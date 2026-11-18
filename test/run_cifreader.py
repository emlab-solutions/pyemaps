'''
Checks for pyEMAPS' CIF reader (pyemaps/cifreader.py), on small CIF texts that each exercise
one CIF 1.1 syntax rule, and on CIF errors.

    python run_cifreader.py        # any arguments (such as ci_sanity's "-bc all") are ignored

Needs no license; runs in CI. Exits 1 if any check fails. Reading real crystal files is
checked by run_features.py, whose CIF corpus results are compared with a baseline.
'''
import os
import sys
import tempfile

RESULTS = []


def check(name, fn):
    try:
        out = fn()
        RESULTS.append((name, True, out or ''))
    except AssertionError as e:
        RESULTS.append((name, False, str(e) or 'assertion failed'))
    except Exception as e:
        RESULTS.append((name, False, f'{type(e).__name__}: {e}'))


def parse(text):
    from pyemaps.cifreader import parse_cif
    return parse_cif(text, 'test.cif')


def refused(text, *words):
    from pyemaps.cifreader import CifSyntaxError
    try:
        parse(text)
    except CifSyntaxError as e:
        missing = [w for w in words if w not in str(e)]
        assert not missing, f'message lacks {missing}: {e}'
        return str(e)
    raise AssertionError('not refused')


def c_items():
    b = parse('data_Si\n_cell_length_a 5.4307(2)\n_cell_angle_alpha 90\n'
              '_symmetry_space_group_name_H-M \'F d -3 m\'\n_unknown ?\n_inapplicable .\n')[0]
    assert b.name == 'Si', b.name
    assert b['_cell_length_a'] == '5.4307(2)' and b['_cell_angle_alpha'] == '90'
    assert b['_symmetry_space_group_name_H-M'] == 'F d -3 m'
    assert b['_unknown'] == '?' and b['_inapplicable'] == '.'
    return 'values, standard uncertainty kept, ? and .'


def c_case():
    b = parse('DATA_x\n_Cell_Length_A 1\n')[0]
    assert b.name == 'x' and '_cell_length_a' in b and b['_CELL_LENGTH_A'] == '1'
    return 'data names and reserved words case-insensitive'


def c_quotes():
    b = parse("data_q\n_a 'it's here'\n_b \"x\"y z\"\n_c 'x'\n_d\t'tab'\n")[0]
    assert b['_a'] == "it's here", b['_a']            # a quote not followed by space continues
    assert b['_b'] == 'x"y z', b['_b']
    assert b['_c'] == 'x' and b['_d'] == 'tab'
    return "'it's here' -> it's here"


def c_text_field():
    b = parse('data_t\n_title\n;Line one\n  line two\n;\n_next 3\n')[0]
    assert b['_title'] == 'Line one\n  line two', repr(b['_title'])
    assert b['_next'] == '3'
    b = parse('data_t\r\n_title\r\n;\r\nA\r\n;\r\n')[0]
    assert b['_title'] == '\nA', repr(b['_title'])
    return 'text field between ";" lines, CRLF line endings'


def c_comments():
    b = parse('# a comment\ndata_c # after the header\n_a 1 # after a value\n'
              "_b 'not # a comment'\n_c x#y\n")[0]
    assert b['_a'] == '1' and b['_b'] == 'not # a comment' and b['_c'] == 'x#y', b.keys()
    return '# outside values only'


def c_loop():
    b = parse('data_l\nloop_\n_atom_site_label\n_atom_site_fract_x\n_atom_site_fract_y\n'
              "Si1 0.125 0.125\nO1 0.5 'x y'\n_after 7\n")[0]
    assert b['_atom_site_label'] == ['Si1', 'O1']
    assert b['_atom_site_fract_y'] == ['0.125', 'x y'] and b['_after'] == '7'
    assert b.loops == [['_atom_site_label', '_atom_site_fract_x', '_atom_site_fract_y']]
    b = parse('data_l\nloop_\n_s\n;text\nvalue\n;\nnext\n')[0]
    assert b['_s'] == ['text\nvalue', 'next'], b['_s']
    return 'columns, quoted and text-field values in loops'


def c_blocks():
    blocks = parse('data_one\n_a 1\ndata_two\n_a 2\n')
    assert [b.name for b in blocks] == ['one', 'two'] and blocks[1]['_a'] == '2'
    b = parse('data_d\nsave_frame\n_x 1\nsave_\n_y 2\n')[0]
    assert '_x' not in b and b['_y'] == '2'
    b = parse('global_\n_g 1\ndata_d\n_y 2\n')[0]
    assert b['_y'] == '2' and '_g' not in b
    return 'several blocks; save frames and global_ skipped'


CIF2 = '#\\#CIF_2.0\n'


def c_cif2():
    b = parse(CIF2 + "data_c2\n_a 'it'\n_b '''multi\nline'''\n_c 4\n_d \"\"\"x\"\"\"\n")[0]
    assert b['_a'] == 'it' and b['_b'] == 'multi\nline' and b['_c'] == '4', b.keys()
    assert b['_d'] == 'x'
    refused(CIF2 + "data_c2\n_a 'it's'\n", 'has no data name')   # ends at the 2nd quote
    refused(CIF2 + "data_c2\n_a 'open\nnext'\n", 'never closed on its line')
    return 'quotes end at the next quote, on their line; triple quotes span lines'


def c_cif2_lists():
    from pyemaps.cifreader import CifList, CifTable
    b = parse(CIF2 + 'data_l\n'
              "_list [1 2 [3 4] 'five six' ?]\n"
              '_table {"a":1 \'b\':[x y] "c":{"d":.}}\n'
              '_multiline [\n  1\n  2 # a comment\n]\n'
              '_empty [ ]\n_empty_table {}\n'
              '_tight [[1][2]{"k":v}]\n'
              '_text\n;\nnot [a list]\n;\n')[0]
    assert b['_list'] == ('1', '2', ('3', '4'), 'five six', '?'), b['_list']
    assert isinstance(b['_list'], CifList) and isinstance(b['_list'][2], CifList)
    assert b['_table'] == {'a': '1', 'b': ('x', 'y'), 'c': {'d': '.'}}, b['_table']
    assert isinstance(b['_table'], CifTable) and isinstance(b['_table']['c'], CifTable)
    assert b['_multiline'] == ('1', '2') and b['_empty'] == () and b['_empty_table'] == {}
    assert b['_tight'] == (('1',), ('2',), {'k': 'v'}), b['_tight']
    assert b['_text'] == '\nnot [a list]', repr(b['_text'])
    return 'nested lists and tables, over lines, without spaces; brackets in text fields are text'


def c_cif2_loops():
    b = parse(CIF2 + 'data_l\nloop_\n_k\n_v\nk1 [1 2]\nk2 {"z":0}\nk3 plain\n')[0]
    assert b['_k'] == ['k1', 'k2', 'k3'], b['_k']
    assert b['_v'] == [('1', '2'), {'z': '0'}, 'plain'], b['_v']
    assert isinstance(b['_v'], list) and not isinstance(b['_v'], tuple)
    return 'lists and tables as looped values; the column is still a plain list'


def c_cif2_errors():
    msgs = [refused(CIF2 + 'data_e\n_a [1 2\n', 'never closed'),
            refused(CIF2 + 'data_e\n_a {"k":1\n', 'never closed'),
            refused(CIF2 + 'data_e\n_a {k:1}\n', 'quoted key'),
            refused(CIF2 + 'data_e\n_a {"k" :1}\n', 'quoted key'),
            refused(CIF2 + 'data_e\n_a {"k":}\n', 'has no value'),
            refused(CIF2 + 'data_e\n_a ["k":1]\n', 'in a list'),
            refused(CIF2 + 'data_e\n_a 1 ]\n', 'never started'),
            refused(CIF2 + 'data_e\n_a x[1]\n', 'has no data name')]   # "[" ends "x"
    return f'{len(msgs)} errors, each with its line'


def c_cif2_crystal():
    '''A crystal written in CIF 2.0, with lists elsewhere, reads as its CIF 1.1 twin.'''
    body = (CELL + 'loop_\n_atom_site_label\n_atom_site_fract_x\n_atom_site_fract_y\n'
            '_atom_site_fract_z\n_atom_site_U_iso_or_equiv\nFe 0 0 0 0.011\nO 0.5 0.5 0.5 0.022\n')
    _, cif1, _ = load('data_twin\n' + body)
    _, cif2, _ = load(CIF2 + 'data_twin\n' + body +
                      '_audit_conform_dict_list [\'cif_core.dic\' "cif_ms.dic"]\n'
                      '_extra {"note":"""a CIF 2.0 table"""}\n')
    assert cif1 == cif2, (cif1, cif2)
    return 'same crystal data as the CIF 1.1 file'


def c_cif1_brackets():
    b = parse('data_c1\n_a x[1]\n_b [1\n_c {k}\n')[0]           # CIF 1.1: brackets are text
    assert (b['_a'], b['_b'], b['_c']) == ('x[1]', '[1', '{k}'), b.keys()
    return 'in CIF 1.1 files, brackets are ordinary characters'


def c_errors():
    msgs = [refused("data_e\n_a 'open\n", 'line 2', 'never closed'),
            refused('data_e\n_a\n;never closed\n', 'text field'),
            refused('data_e\nloop_\n_a\n_b\n1 2 3\n', 'not a whole number of rows'),
            refused('data_e\n_a 1\n_a 2\n', 'appears twice'),
            refused('data_e\nstray\n', 'has no data name'),
            refused('_a 1\n', 'before the first data block'),
            refused('data_e\n_a\n_b 2\n', '_a has no value'),
            refused('data_e\nsave_x\n_a 1\n', 'never closed')]
    return f'{len(msgs)} errors, each with its line'


def c_file():
    from pyemaps.cifreader import read_cif
    with tempfile.TemporaryDirectory() as tmp:
        fn = os.path.join(tmp, 'latin.cif')
        with open(fn, 'wb') as f:
            f.write(b'data_l\n_name \'\xc5ngstr\xf6m\'\n')        # Latin-1, not UTF-8
        b = read_cif(fn)[0]
        assert b['_name'] == '\xc5ngstr\xf6m', b['_name']
        fn = os.path.join(tmp, 'bom.cif')
        with open(fn, 'wb') as f:
            f.write(b'\xef\xbb\xbfdata_b\n_x 1\n')
        assert read_cif(fn)[0].name == 'b'
    return 'UTF-8 with BOM and Latin-1 files'


def c_from_cif():
    from pyemaps import Crystal
    here = os.path.dirname(os.path.abspath(__file__))
    si = Crystal.from_cif(os.path.join(here, 'cifdata', '1010100.cif'))
    assert si.name == '1010100', si.name
    return f'{si.name}: {len(si.atoms)} atoms'


CELL = '''_cell_length_a 4.0
_cell_length_b 4.0
_cell_length_c 4.0
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 90
_symmetry_Int_Tables_number 221
'''


def load(text):
    '''loadCrystalCIFData on CIF text: (name, data, printed output).'''
    import io
    from contextlib import redirect_stdout
    from pyemaps import fileutils
    with tempfile.TemporaryDirectory() as tmp:
        fn = os.path.join(tmp, 't.cif')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(text)
        buf = io.StringIO()
        with redirect_stdout(buf):
            name, data = fileutils.loadCrystalCIFData(fn)
    return name, data, buf.getvalue()


def c_uiso_variant():
    _, data, _ = load('data_v\n' + CELL + 'loop_\n_atom_site_label\n_atom_site_fract_x\n'
                      '_atom_site_fract_y\n_atom_site_fract_z\n_atom_site_Uiso_or_equiv\n'
                      'Fe 0 0 0 0.011\nO 0.5 0.5 0.5 0.022\n')
    fe, o = data['atoms']
    assert data['dw'] == 'uij', data['dw']
    assert (fe['b11'], fe['b22'], fe['b33'], fe['b12']) == (0.011, 0.011, 0.011, 0.0), fe
    assert o['b33'] == 0.022, o
    return '_atom_site_Uiso_or_equiv read like _atom_site_U_iso_or_equiv'


def c_aniso_by_label():
    text = ('data_a\n' + CELL +
            'loop_\n_atom_site_label\n_atom_site_type_symbol\n_atom_site_fract_x\n'
            '_atom_site_fract_y\n_atom_site_fract_z\n_atom_site_U_iso_or_equiv\n'
            'Fe1 Fe 0 0 0 0.010\nO1 O 0.5 0.5 0.5 0.020\nH1 H 0.25 0.25 0.25 0.050\n'
            # the anisotropic table lists O1 then Fe1, and not H1
            'loop_\n_atom_site_aniso_label\n_atom_site_aniso_U_11\n_atom_site_aniso_U_22\n'
            '_atom_site_aniso_U_33\n_atom_site_aniso_U_12\n_atom_site_aniso_U_13\n'
            '_atom_site_aniso_U_23\n'
            'O1 0.021 0.022 0.023 0.001 0.002 0.003\n'
            'Fe1 0.011 0.012 0.013 0.004 0.005 0.006\n'
            'X9 0.9 0.9 0.9 0 0 0\n')
    _, data, out = load(text)
    fe, o, h = data['atoms']
    assert data['dw'] == 'uij', data['dw']
    assert [fe[k] for k in ('b11', 'b22', 'b33', 'b12', 'b13', 'b23')] == \
        [0.011, 0.012, 0.013, 0.004, 0.005, 0.006], fe
    assert [o[k] for k in ('b11', 'b22', 'b33', 'b12', 'b13', 'b23')] == \
        [0.021, 0.022, 0.023, 0.001, 0.002, 0.003], o
    assert [h[k] for k in ('b11', 'b22', 'b33', 'b12', 'b13', 'b23')] == \
        [0.05, 0.05, 0.05, 0.0, 0.0, 0.0], h                  # its isotropic U, not 0
    assert 'X9' in out and 'ignored' in out, out
    return 'Fe1, O1 by label (listed in another order); H1 keeps its U_iso; unknown X9 ignored'


def c_aniso_b():
    text = ('data_b\n' + CELL +
            'loop_\n_atom_site_label\n_atom_site_fract_x\n_atom_site_fract_y\n'
            '_atom_site_fract_z\n_atom_site_B_iso_or_equiv\n'
            'Fe 0 0 0 0.5\nO 0.5 0.5 0.5 0.7\n'
            'loop_\n_atom_site_aniso_label\n_atom_site_aniso_B_11\n_atom_site_aniso_B_22\n'
            '_atom_site_aniso_B_33\nO 0.61 0.62 0.63\n')
    _, data, _ = load(text)
    fe, o = data['atoms']
    assert data['dw'] == 'bij', data['dw']
    assert (o['b11'], o['b22'], o['b33']) == (0.61, 0.62, 0.63), o
    assert (fe['b11'], fe['b22'], fe['b33']) == (0.5, 0.5, 0.5), fe
    return 'B tables matched by label too; Fe keeps its B_iso'


def c_single_atom():
    _, data, _ = load('data_s\n' + CELL + '_atom_site_label Fe\n_atom_site_fract_x 0\n'
                      '_atom_site_fract_y 0\n_atom_site_fract_z 0\n_atom_site_occupancy 1.0\n'
                      '_atom_site_B_iso_or_equiv 0.4\n')
    assert len(data['atoms']) == 1, data['atoms']
    at = data['atoms'][0]
    assert at['symb'] == 'FE' or at['symb'].upper() == 'FE', at
    assert at['d-w'] == 0.4 and at['occ'] == 1.0, at
    return 'one atom written without loop_'


def c_real_cod():
    '''Real COD structures: every atom's displacement values, by its own label.'''
    import re
    from pyemaps.cifreader import read_cif
    num = re.compile(r'[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?')

    def value(v):
        m = num.search(v)
        return float(m.group(0)) if m else 0.0

    def col(b, key):
        v = b[key]
        return v if isinstance(v, list) else [v]

    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cifcases')
    names = sorted(f for f in os.listdir(folder) if f.endswith('.cif'))
    assert len(names) == 3, names
    notes = []
    for name in names:
        fn = os.path.join(folder, name)
        b = read_cif(fn)[0]
        labels = col(b, '_atom_site_label')
        iso = [value(v) for v in col(b, '_atom_site_U_iso_or_equiv')]
        expected = [[x, x, x, 0.0, 0.0, 0.0] for x in iso]
        aniso = col(b, '_atom_site_aniso_label')
        for r, lab in enumerate(aniso):
            for c, k in enumerate(('11', '22', '33', '12', '13', '23')):
                expected[labels.index(lab)][c] = value(col(b, f'_atom_site_aniso_U_{k}')[r])
        _, data, _ = load(open(fn, encoding='utf-8').read())
        got = [[a[f'b{k}'] for k in ('11', '22', '33', '12', '13', '23')] for a in data['atoms']]
        assert data['dw'] == 'uij' and len(got) == len(labels), (name, data['dw'], len(got))
        wrong = [labels[i] for i in range(len(labels)) if got[i] != expected[i]]
        assert not wrong, f'{name}: wrong displacement parameters for {wrong[:5]}'
        notes.append(f'{name[:-4]} ({len(aniso)} of {len(labels)} atoms anisotropic)')
    return ', '.join(notes)


def main():
    for name, fn in (('data items and special values', c_items),
                     ('case-insensitive names and reserved words', c_case),
                     ('quoted values', c_quotes),
                     ('text fields', c_text_field),
                     ('comments', c_comments),
                     ('loops', c_loop),
                     ('several data blocks, save frames, global_', c_blocks),
                     ('CIF 2.0 quoting', c_cif2),
                     ('CIF 2.0 lists and tables', c_cif2_lists),
                     ('CIF 2.0 lists and tables in loops', c_cif2_loops),
                     ('CIF 2.0 syntax errors', c_cif2_errors),
                     ('a CIF 2.0 crystal file', c_cif2_crystal),
                     ('CIF 1.1 files keep brackets as text', c_cif1_brackets),
                     ('syntax errors are refused with their line', c_errors),
                     ('file encodings', c_file),
                     ('Crystal.from_cif reads a corpus file', c_from_cif),
                     ('_atom_site_Uiso_or_equiv is read (it crashed before)', c_uiso_variant),
                     ('anisotropic U matched to atoms by label', c_aniso_by_label),
                     ('anisotropic B matched to atoms by label', c_aniso_b),
                     ('a single atom written without loop_', c_single_atom),
                     ('real COD structures: displacement parameters by label', c_real_cod)):
        check(name, fn)
    for name, ok, msg in RESULTS:
        print(f'{"PASS" if ok else "FAIL"}  {name}: {msg}')
    failed = [r for r in RESULTS if not r[1]]
    if failed:
        print(f'------ CIF reader checks FAILED: {len(failed)} of {len(RESULTS)} ------')
        return 1
    print(f'++++++ CIF reader checks SUCCEEDED: {len(RESULTS)} checks ++++++')
    return 0


if __name__ == '__main__':
    os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
    sys.exit(main())
