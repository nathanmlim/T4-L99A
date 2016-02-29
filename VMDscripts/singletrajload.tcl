proc loadrepl {ci cdir sta fin} {
   set fepdir /media/limn1/SG1TB/Projects/LigFEP_T4/COMPLETE_SETUP/FEP_SCHOLAR/
   set cpath ${fepdir}${cdir}/fep_scholar_${ci}/fep_scholar_${ci}_fep1/fep_scholar_${ci}_2/fep_scholar_${ci}_complex_fep1/fep_scholar_${ci}_complex_10

   #Check if the parent trajectory path exists
   if {[file isdirectory $cpath]} {
      #Get list of cms files
      set cms [glob -directory $cpath -type f *{${ci}-out.cms}]
      set trj [glob -directory $cpath *{${ci}_trj}]
      set dtr [glob -directory $trj -type f *{dtr}]
      
      #Load cms file/trajectories
      mol new ${cms} type {mae} first $sta last $fin step 1 waitfor all
      mol addfile ${dtr} type {dtr} first $sta last $fin step 1 waitfor all
      set repmolid [molinfo top get id]
      mol rename $repmolid Replica${ci}

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

      #Select trajectory we are comparing and loop over frames
      set traj [atomselect $repmolid "backbone and resid 77 to 120 and not resid 107 to 115"]
      set num_frames [molinfo $repmolid get numframes]
      
      for {set frame 0} {$frame < $num_frames} {incr frame} {
         #Get the correct frame
         $traj frame $frame

         #Compute transformation matrix to closed state
         set M [measure fit $traj $refc]
         #Align to closed state
         set move_sel [atomselect $repmolid "all" frame $frame]
         $move_sel move $M

         #Compute RMSD of F-helix to crystal structures
         #Change our atom selection
         set comp [atomselect $repmolid "(backbone and resid 107 to 115) and name C CA N" frame $frame]
         set chelix [atomselect $conf_c "(backbone and resid 107 to 115) and name C CA N" frame 0]
         set ihelix [atomselect $conf_i "(backbone and resid 107 to 115) and name C CA N" frame 0]
         set ohelix [atomselect $conf_o "(backbone and resid 107 to 115) and name C CA N" frame 0]

         set rmsdc [measure rmsd $comp $chelix]
         set rmsdi [measure rmsd $comp $ihelix]
         set rmsdo [measure rmsd $comp $ohelix]
         
         lappend rmsd_list (${frame} ${rmsdc} ${rmsdi} ${rmsdo})
         }

   #output our RMSD values
   puts $rmsd_list
   } else {
      puts "Did not find trajectory directory, untaring trajectories"
      set tarloc [file join {*}[lrange [file split $cpath] 0 end-2]]
      set tarfile [glob -directory $tarloc -type f *{complex_10-out.tgz}]
      puts $tarfile
      exec tar -xvzf $tarfile --directory $tarloc
   }
}


loadrepl 2 c_exp_opls3 0 209
