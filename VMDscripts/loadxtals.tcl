#Load in Crystal Structures
mol new {/media/limn1/SG1TB/Projects/LigFEP_T4/COMPLETE_SETUP/input_structures/prepped_PDB/4W53_toluene_closed.mae} type {mae} first 0 last -1 step 1 waitfor 1
set conf_c [molinfo top get id]
puts $conf_c

mol new {/media/limn1/SG1TB/Projects/LigFEP_T4/COMPLETE_SETUP/input_structures/prepped_PDB/4W57_nbutyl_int.mae} type {mae} first 0 last -1 step 1 waitfor 1
set conf_i [molinfo top get id]
puts $conf_i

mol new {/media/limn1/SG1TB/Projects/LigFEP_T4/COMPLETE_SETUP/input_structures/prepped_PDB/4W59_nhexyl_open.mae} type {mae} first 0 last -1 step 1 waitfor 1
set conf_o [molinfo top get id]
puts $conf_o

#Change representation to NewRibbons
mol modstyle 0 $conf_c NewRibbons 0.300000 12.000000 3.000000 0
mol modstyle 0 $conf_i NewRibbons 0.300000 12.000000 3.000000 0
mol modstyle 0 $conf_o NewRibbons 0.300000 12.000000 3.000000 0

#Display only select range of residues (F-Helix)
mol modselect 0 $conf_c resid 104 to 120
mol modselect 0 $conf_i resid 104 to 120
mol modselect 0 $conf_o resid 104 to 120

#Color entries by xtal structure (C,I,O)
mol modcolor 0 $conf_c ColorID 11 
mol modcolor 0 $conf_i ColorID 10
mol modcolor 0 $conf_o ColorID 7

#Display xtal ligand positions
mol addrep $conf_c
mol modselect 1 $conf_c resid 200
mol modstyle 1 $conf_c Lines 1.000000
mol modcolor 1 $conf_c ColorID 11
mol addrep $conf_i
mol modselect 1 $conf_i resid 200
mol modstyle 1 $conf_i Lines 1.000000
mol modcolor 1 $conf_i ColorID 10

mol addrep $conf_o
mol modselect 1 $conf_o resid 200
mol modstyle 1 $conf_o Lines 1.000000
mol modcolor 1 $conf_o ColorID 7

display resetview
