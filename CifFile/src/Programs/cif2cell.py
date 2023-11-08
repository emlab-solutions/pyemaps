# A simple and limited example program for converting CIF files
# to PowderCell .cel files, according to the specification at 
# http://www.ccp14.ac.uk/ccp/web-mirrors/powdcell/a_v/v_1/powder/details/powcell.htm

# Limitations:
# 1. Non-standard settings not handled
# 2. No occupancy or isotropic displacement included 
# 3. Only atoms with an entry in the table below can be handled.

atom_type_table = {
    'H':1,
    'He':2,
    'C':6,
    'O':8,
    'Al':13,
     #Add more as necessary
     }


from CifFile import CifFile, get_number_with_esd
import sys

gnwe = get_number_with_esd # for brevity
def transform(my_cif_file):
    """Turn a CIF file into a CEL file"""
    cf = CifFile(my_cif_file).first_block()
    outfile = open(my_cif_file+".cel","w") 
    # Write out the cell parameters
    outfile.write("CELL ")
    cell_parms =   ['_cell_length_a',
                    '_cell_length_b',
                    '_cell_length_c',
                    '_cell_angle_alpha',
                    '_cell_angle_beta',
                    '_cell_angle_gamma']
    #Strip off any appended SU
    cell_parms = [gnwe(cf[a])[0] for a in cell_parms]
    [outfile.write("%f " % a) for a in cell_parms]
    outfile.write("\n") 
    # Write out the atomic parameters
    atom_loop = cf.GetLoop('_atom_site_label')
    for a in atom_loop:
        # Work out atomic number
        at_type = a._atom_site_type_symbol
        t = atom_type_table.get(at_type)
        if t is None:
            print "Error: do not know atomic number for " + at_type
            print "Please add an entry to the table."
            return
        outfile.write("%s %d %f %f %f\n" % (a._atom_site_label,
                                            t,
                                        gnwe(a._atom_site_fract_x)[0],
                                        gnwe(a._atom_site_fract_y)[0],
                                        gnwe(a._atom_site_fract_z)[0]))
    # Write out the space group information
    outfile.write("RGNR ")
    sg = cf.get('_space_group_IT_number',
         cf.get('_symmetry_Int_Tables_number'))
    if sg is None:
        sgname = cf.get('_space_group_name_H-M',
                 cf.get('_symmetry_space_group_name_H-M','?'))
        print """No space group number in file, you will have to insert
                 the number by hand for space group """ + sgname
        print "Software will put xxx instead"
        outfile.write("xxx")
    else:
        outfile.write("%s" % sg)
    outfile.write("\n")
    outfile.close()

if __name__ == '__main__':
    if len(sys.argv)< 2:
        print "Usage: cif2cel <filename>"
    else:
        transform(sys.argv[1])
