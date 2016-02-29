#Set general working directory and job number of each respectable job
set ci 2
set oi 1
set cpi 1
set opi 1
set cdir c_exp_opls3
set odir o_opls3
set cpdir c_opls3_rest1
set opdir o_opls3_rest1
#Set timepoints, framenum * 23 = Xns
set sta 0
set fin 209

#Set our paths for the trajectories
set fepdir /media/limn1/SG1TB/Projects/LigFEP_T4/COMPLETE_SETUP/FEP_SCHOLAR/
set cpath ${fepdir}${cdir}/fep_scholar_${ci}/fep_scholar_${ci}_fep1/fep_scholar_${ci}_2/fep_scholar_${ci}_complex_fep1/fep_scholar_${ci}_complex_10/
set opath ${fepdir}${odir}/fep_scholar_${oi}/fep_scholar_${oi}_fep1/fep_scholar_${oi}_2/fep_scholar_${oi}_complex_fep1/fep_scholar_${oi}_complex_10/
set cppath ${fepdir}${cpdir}/fep_scholar_${cpi}/fep_scholar_${cpi}_fep1/fep_scholar_${cpi}_2/fep_scholar_${cpi}_complex_fep1/fep_scholar_${cpi}_complex_10/
set oppath ${fepdir}${opdir}/fep_scholar_${opi}/fep_scholar_${opi}_fep1/fep_scholar_${opi}_2/fep_scholar_${opi}_complex_fep1/fep_scholar_${opi}_complex_10/

#Check if the parent trajectory path exists
#set path_list [list $cpath $opath $cppath $oppath]
set path_list [list $cpath]
foreach path $path_list {
   
   if {[file isdirectory $path]} {
      #Get list of cms files
      set cms [lsort -dictionary [glob -directory $path -type f *{-out.cms}]]
      set trj [lsort -dictionary [glob -directory $path *{trj}]]

      set index -1
      foreach t $trj c $cms {
         incr index
         #Get list of trajectory.dtr
         set dtr [glob -directory $t -type f *{dtr}]

         #Load cms file/trajectories
         mol new ${c} type {mae} first $sta last $fin step 1 waitfor all
         mol addfile ${dtr} type {dtr} first $sta last $fin step 1 waitfor all
         set repl($index) [molinfo top get id]
         puts $repl($index)
         mol rename $repl($index) rep$index

         #Set viewing preferences for protein
         mol modselect 0 $repl($index) resid 104 to 120 and not water
         mol modstyle 0 $repl($index) NewRibbons 0.300000 12.000000 3.000000 0
         mol modcolor 0 $repl($index) ColorID 8
         #Set viewing preferences for ligand
         mol addrep $repl($index)
         mol modselect 1 $repl($index) resid 200 and not water
         mol modstyle 1 $repl($index) Licorice 0.300000 12.000000 12.000000
         mol modcolor 1 $repl($index) ColorID 8
         
         #Set our frame of reference, aligning by protein surrouding F-helix
         set refc [atomselect $conf_c "backbone and resid 77 to 120 and not resid 107 to 115" frame 0]
         set refi [atomselect $conf_i "backbone and resid 77 to 120 and not resid 107 to 115" frame 0]
         set refo [atomselect $conf_o "backbone and resid 77 to 120 and not resid 107 to 115" frame 0]
         #Select trajectory we are comparing and loop over frames
         set traj [atomselect $repl($index) "backbone and resid 77 to 120 and not resid 107 to 115"]
         set num_frames [molinfo $repl($index) get numframes]
         for {set frame 0} {$frame < $num_frames} {incr frame} {
            #Get the correct frame
            $traj frame $frame

            #Compute transformation matrix to closed state
            set M [measure fit $traj $refc]
            #Align to closed state
            set move_sel [atomselect $repl($index) "all" frame $frame]
            $move_sel move $M

            #Compute RMSD of F-helix to crystal structures
            #Change our atom selection
            set comp [atomselect $repl($index) "(backbone and resid 107 to 115) and name C CA N" frame $frame]
            set chelix [atomselect $conf_c "(backbone and resid 107 to 115) and name C CA N" frame 0]
            set ihelix [atomselect $conf_i "(backbone and resid 107 to 115) and name C CA N" frame 0]
            set ohelix [atomselect $conf_o "(backbone and resid 107 to 115) and name C CA N" frame 0]

            set rmsdc [measure rmsd $comp $chelix]
            set rmsdi [measure rmsd $comp $ihelix]
            set rmsdo [measure rmsd $comp $ohelix]

            puts "RMSD of $frame is $rmsdc"

         }

         if {$index == 0} break
      }
   } else {
      puts "Did not find trajectory directory, untaring trajectories"
      #set tarloc [file join {*}[lrange [file split $path] 0 end-2]]
      #set tarfile [glob -directory $tarloc -type f *{complex_10-out.tgz}]
      #puts $tarfile
      #exec tar -xvzf $tarfile --directory $tarloc
   }
}

