# Real CIF test cases

Real crystal structures, checked by `test/run_cifreader.py`: each atom's displacement
parameters must be the file's values for that atom's own label. They're kept apart from
`test/cifdata`, whose files are also simulated and compared with baselines by
`run_features.py`.

Each has an anisotropic displacement table (`_atom_site_aniso_*`) that doesn't list the atoms
the way the atom site table does, as in most published structures with hydrogen atoms:

| File | Structure | Anisotropic table |
|---|---|---|
| `2200018.cif` | C6 H11 N O2 (Acta Cryst. E, 2001) | 9 of 20 atoms, in a different order |
| `2200017.cif` | C8 H14 N2 (Acta Cryst. E, 2001) | the non-hydrogen atoms; 14 hydrogens left out |
| `4000009.cif` | C4 H18 Mn N4 O12 V4 (Chem. Mater., 2000) | 13 of 22 atoms, a different subset |

pyEMAPS 2.3.0 gave atoms other atoms' values for all three.

## Source and license

From the Crystallography Open Database (COD), <https://www.crystallography.net/cod/>, entries
2200018, 2200017 and 4000009, unchanged. COD: "All data in the COD and the database itself are
dedicated to the public domain and licensed under the CC0 License."
