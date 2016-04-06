proc loadrepl {path jobnum repnum sta fin} {
   set fepdir /media/limn1/SG1TB1/Projects/LigFEP_T4/COMPLETE_SETUP/FEP_SCHOLAR/
   set cpath ${fepdir}${path}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_10

   #Check if the parent trajectory path exists
   if {[file isdirectory $cpath]} {
      #Get paths of cms/trj files
      set cms [glob -directory $cpath -type f "*replica${repnum}-out.cms"]
      set ene [glob -directory $cpath -type f "*replica${repnum}.ene"]
      set trj [glob -directory $cpath "*replica${repnum}_trj"]
      set dtr [glob -directory $trj -type f *{dtr}]
      
      
      #Parse the ene file
      #while {[gets $enefile line] >= 0} {
      #   if {[string match "#*" $line]} {
           #Pass over comments
      #     continue 
      #   }
      #   set contents [split $line "\n"]
         #set test [regexp -inline -all -- {\S+} $contents]
      #   foreach ele $contents {
      #      puts [lindex [regexp -inline -all {\S+} $ele]]
      #   }
      #}
      

      puts "Loading ${path}_${jobnum}-replica${repnum}"
      #Load cms file/trajectories
      mol new ${cms} type {mae} first $sta last $fin step 1 waitfor 1
      mol addfile ${dtr} type {dtr} first $sta last $fin step 1 waitfor all
      set repmolid [molinfo top get id]
      mol rename $repmolid Replica${repnum}

      #Set viewing preferences for protein
      mol modselect 0 $repmolid resid 104 to 120 and not water
      mol modstyle 0 $repmolid NewRibbons 0.300000 12.000000 3.000000 0
      mol modcolor 0 $repmolid ColorID 8
      
      #Set viewing preferences for ligand
      mol addrep $repmolid
      mol modselect 1 $repmolid resid 200 and not water
      mol modstyle 1 $repmolid Licorice 0.300000 12.000000 12.000000
      mol modcolor 1 $repmolid ColorID 8

      #Get molid for xtal structures
      set molidlist [molinfo list]
      foreach molid $molidlist {
         set molname [molinfo $molid get name]
         if {[string match closed* $molname]} {
            set conf_c $molid
         }
         if {[string match int* $molname]} {
            set conf_i $molid
         }
         if {[string match open* $molname]} {
            set conf_o $molid
         }
      }

      #Set our frame of reference, aligning by protein surrouding F-helix
      set refc [atomselect $conf_c "backbone and resid 77 to 120 and not resid 107 to 115" frame 0]
      set refi [atomselect $conf_i "backbone and resid 77 to 120 and not resid 107 to 115" frame 0]
      set refo [atomselect $conf_o "backbone and resid 77 to 120 and not resid 107 to 115" frame 0]
      set ligrefo [atomselect $conf_o "resid 200 and not water" frame 0]
      puts [$ligrefo num]

      #Select trajectory we are comparing and loop over frames
      set traj [atomselect $repmolid "backbone and resid 77 to 120 and not resid 107 to 115"]
      set num_frames [molinfo $repmolid get numframes]
      
      
      #Initialize output for writing RMSD
      file mkdir ${path}_${jobnum}
      set output [open ./${path}_${jobnum}/replica${repnum}.rmsd w]
      file copy -force $ene ./${path}_${jobnum}/replica${repnum}.ene
      puts $output "FrameNum Closed Int Open" 
      
      #Loop over trajectory frames
      for {set frame 0} {$frame < $num_frames} {incr frame} {
         #Get the correct frame
         $traj frame $frame

         #Compute transformation matrix for alignment
         #Set our reference to closed state
         set M [measure fit $traj $refc]
         set move_sel [atomselect $repmolid "all" frame $frame]
         $move_sel move $M

         #Change our atom selection to F-helix backbone atoms
         set comp [atomselect $repmolid "(backbone and resid 107 to 115) and name C CA N" frame $frame]
         set chelix [atomselect $conf_c "(backbone and resid 107 to 115) and name C CA N" frame 0]
         set ihelix [atomselect $conf_i "(backbone and resid 107 to 115) and name C CA N" frame 0]
         set ohelix [atomselect $conf_o "(backbone and resid 107 to 115) and name C CA N" frame 0]
         set ligtraj [atomselect $repmolid "resid 200 and not water" frame $frame]  

         #Compute RMSD of F-helix to crystal structures
         set rmsdc [measure rmsd $comp $chelix]
         set rmsdi [measure rmsd $comp $ihelix]
         set rmsdo [measure rmsd $comp $ohelix]

         #if {$repnum == 11 } {
            #puts [$ligtraj num]
            #set ligrmsd [measure rmsd $ligtraj $ligrefo]
          #  puts $ligrmsd
          #  puts $output "${frame} ${rmsdc} ${rmsdi} ${rmsdo} ${ligrmsd}"
         #} else {
        puts $output "${frame} ${rmsdc} ${rmsdi} ${rmsdo}"
          #}
   }

   close $output
   mol delete $repmolid

      
   } else {
      puts "Did not find trajectory directory, untaring trajectories"
      set tarloc [file join {*}[lrange [file split $cpath] 0 end-2]]
      set tarfile [glob -directory $tarloc -type f *{complex_10-out.tgz}]
      puts $tarfile
      exec tar -xvzf $tarfile --directory $tarloc
   }
}


#loadrepl {path jobnum repnum sta fin}
for {set repnum 0} { $repnum < 12} {incr repnum} {
   loadrepl c_exp_opls3 11 $repnum 0 210
   loadrepl o_exp_opls3 24 $repnum 0 210
   #loadrepl o_exp_opls3 17 $repnum 0 210
   #loadrepl c_exp_opls3_rest1 7e $repnum 0 1042
   #loadrepl o_exp_opls3_rest1 7 $repnum 0 1042
}

quit
