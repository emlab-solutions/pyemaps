# find cell value for all builtin crystals

#  Crystal volume:    66.3956857031570     
#  Crystal volume:    254.970813822399     
#  Crystal volume:    66.3956857031570
#  Crystal volume:    64.2060061737537
#  Crystal volume:    128.760668269974
#  Crystal volume:    64.3165926719680     
#  Crystal volume:    946.686020845500
#  Crystal volume:    387.406250000000
#  Crystal volume:    112.197592972325
#  Crystal volume:    196.934203432000
#  Crystal volume:    99.4508132898117
#  Crystal volume:    24.0374824560000     
#  Crystal volume:    81.4995811169037
#  Crystal volume:    47.2416333750000
#  Crystal volume:    737.783038656000     
#  Crystal volume:    77.7724637691250     
#  Crystal volume:    45.3846852630000
#  Crystal volume:    244.781620320000
#  Crystal volume:    135.098972919412
#  Crystal volume:    397.541031774086
#  Crystal volume:    101.157131683745
#  Crystal volume:    127.197990302536
#  Crystal volume:    146.529883648000
#  Crystal volume:    685.154755623294
#  Crystal volume:    160.164933272443
#  Crystal volume:    59.3007498719360
#  Crystal volume:    175.980208470880
#  Crystal volume:    71.4347910035640
#  Crystal volume:    136.267993270575
#  Crystal volume:    62.4232992981957
#  Crystal volume:    120.896237942300
#  Crystal volume:    546.115598913940
#  Crystal volume:    47.3162241975636
#  Crystal volume:    30.4275488814749
#  Crystal volume:    95.6320805170000

from pyemaps import Crystal as cr
from pyemaps import dif

lcrystals = cr.list_all_builtin_crystals()

for cn in lcrystals:
    c = cr.from_builtin(cn)
    cell, atoms, atn, spg = c.prepareDif()
    ret = dif.loadcrystal(cell, atoms, atn, spg, ndw=c._dw)
    
    if ret == -1:
        print(f'------- Cell volume for {cn} exceeded 500 -------')




