#Set general working directory and job number of each respectable job
set ci 1
set oi 1
set cpi 1
set opi 1
set cdir c_opls3
set odir o_opls3
set cpdir c_opls3_rest1
set opdir o_opls3_rest1

#Set our paths for the trajectories
set fepdir /media/limn1/SG1TB/Projects/LigFEP_T4/COMPLETE_SETUP/FEP_SCHOLAR/
set cpath ${fepdir}${cdir}/fep_scholar_${ci}/fep_scholar_${ci}_fep1/fep_scholar_${ci}_2/fep_scholar_${ci}_complex_fep1/fep_scholar_${ci}_complex_10/
set opath ${fepdir}${odir}/fep_scholar_${oi}/fep_scholar_${oi}_fep1/fep_scholar_${oi}_2/fep_scholar_${oi}_complex_fep1/fep_scholar_${oi}_complex_10/
set cppath ${fepdir}${cpdir}/fep_scholar_${cpi}/fep_scholar_${cpi}_fep1/fep_scholar_${cpi}_2/fep_scholar_${cpi}_complex_fep1/fep_scholar_${cpi}_complex_10/
set oppath ${fepdir}${opdir}/fep_scholar_${opi}/fep_scholar_${opi}_fep1/fep_scholar_${opi}_2/fep_scholar_${opi}_complex_fep1/fep_scholar_${opi}_complex_10/

#Check if the parent trajectory path exists
set path_list [list $cpath $opath $cppath $oppath]
foreach path $path_list {
   
   if {[file isdirectory $path]} {
      #Get list of cms files
      set cms [lsort [glob -directory $path -type f *{-out.cms}]]
      
      puts $cms
   } else {
      puts "Did not find trajectory directory, untaring trajectories"
      set tarloc [file join {*}[lrange [file split $path] 0 end-2]]
      set tarfile [glob -directory $tarloc -type f *{complex_10-out.tgz}]
      puts $tarfile
      exec tar -xvzf $tarfile --directory $tarloc
   }
}

