# A program to add key names to CIF categories that
# only have _category.key_id
from CifFile import CifDic

def add_keynames(inname):
    """ Add '_category_key.name' loop to all
    categories that only have '_category.key_id' """
    outname = inname + ".out"
    indic = CifDic(inname,grammar="2.0",do_minimum=True)
    cats = [k for k in indic.keys() if indic[k].get("_definition.scope","Item") == "Category"]
    cats = [k for k in cats if indic[k].get("_definition.class","Set") == "Loop"]
    bad_cats = [c for c in cats if len(indic[c].get('_category_key.name',[])) == 0]
    for b in bad_cats:
        print 'Adding to category %s'% b
        indic[b]['_category_key.name'] = [indic[b]['_category.key_id']]
        indic[b].CreateLoop(['_category_key.name'])
    indic.SetTemplate("dic_template.dic")
    outtext = indic.WriteOut()
    p = open(outname,"w")
    p.write(outtext)
    p.close()
    
if __name__=="__main__":
    import sys
    dicname = sys.argv[1]
    add_keynames(dicname)
    
