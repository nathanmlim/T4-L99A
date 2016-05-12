copy_job () {
rsync -avhWP --no-compress    \
   --exclude='*multisim*'     \
   --exclude='*_1-out.tgz'    \
   --exclude='*_2-out.tgz'    \
   --exclude='*_3-out.tgz'    \
   --exclude='*_10-out.tgz'   \
   --exclude='*_11-out.tgz'   \
   --exclude='*-out.mae'      \
   --exclude='*_complex_fep1' \
   --exclude='*_solvent_fep1' \
   --include="$source/$setname/fep_scholar_$jobnum/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_12-out.tgz"  \
   --include="$source/$setname/fep_scholar_$jobnum/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_solvent_13-out.tgz"  \
   $source/$setname/fep_scholar_$jobnum $dest
}

untar_output () {
innersource="$dest/fep_scholar_$jobnum/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2"
tar -C $innersource -xzf $innersource/fep_scholar_${jobnum}_complex_12-out.tgz 
tar -C $innersource -xzf $innersource/fep_scholar_${jobnum}_solvent_13-out.tgz
rm $innersource/fep_scholar_${jobnum}_complex_12-out.tgz
rm $innersource/fep_scholar_${jobnum}_solvent_13-out.tgz
rm $innersource/*checkpoint*
}


results () {
#cmd_1="/home/limn1/opt/schrodinger2015-4/run -FROM desmond bennett.py -b 0 -e 5000 l 0 -L 11 -s ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/gibbs.%d.dE -o ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result_0-5ns"
#cmd_2="/home/limn1/opt/schrodinger2015-4/run -FROM desmond bennett.py -b 40000 -e 55000 l 0 -L 11 -s ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/gibbs.%d.dE -o ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result_40-55ns"
#cmd_3="rm ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result"
#eval $cmd_1
#eval $cmd_2
#eval $cmd_3
   
complex=$(tail -1 ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result | awk {'print $4'} | grep .[0-9]*)
comp_err=$(tail -1 ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result | awk {'print $6'} | grep .[0-9]*)
solvent=$(tail -1 ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_solvent_fep1/fep_scholar_${jobnum}_solvent_13/result | awk {'print $4'} | grep .[0-9]*)
sol_err=$(tail -1 ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_solvent_fep1/fep_scholar_${jobnum}_solvent_13/result | awk {'print $6'} | grep .[0-9]*)
#complex1=$(tail -1 ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result_40-55ns | awk {'print $4'} | grep .[0-9]*)
#comp_err1=$(tail -1 ${dest}/fep_scholar_${jobnum}/fep_scholar_${jobnum}_fep1/fep_scholar_${jobnum}_2/fep_scholar_${jobnum}_complex_fep1/fep_scholar_${jobnum}_complex_12/result_40-55ns | awk {'print $6'} | grep .[0-9]*)

#echo $complex $comp_err $solvent $sol_err
ddG=$(echo "${complex} - ${solvent}" | bc | xargs printf "%.*f\n" 2)
sigma=$(echo "sqrt( (${comp_err}*${comp_err} + ${sol_err}*${sol_err}))" | bc | xargs printf "%.*f\n" 2)
echo "0-5ns: ddG=$ddG+-$sigma"

#ddG1=$(echo "${complex1} - ${solvent}" | bc | xargs printf "%.*f\n" 2)
#sigma1=$(echo "sqrt( (${comp_err1}*${comp_err1} + ${sol_err}*${sol_err}))" | bc | xargs printf "%.*f\n" 2)
#echo "40-55ns: ddG=$ddG1+-$sigma1"


txt="Start Conf: $conf
Ligands: $dirname
Protocol: Default
FF: OPLS3
Set: Experimental
dG_complex(0-5ns): $(printf "%.*f\n" 2 ${complex})+-$(printf "%.*f\n" 2 ${comp_err})
dG_solvent: $(printf "%.*f\n" 2 ${solvent})+-$(printf "%.*f\n" 2 ${sol_err})
ddG(0-5ns): $ddG+-$sigma"

echo "$txt" > $dest/fep_scholar_$jobnum/README.txt
}

while getopts 'j:s:n:c:' option
do
   case $option in
      j ) jobnum=$OPTARG;;
      s ) setname=$OPTARG;;
      n ) dirname=$OPTARG;;
      c ) conf=$OPTARG;;
   esac
done

source="/media/limn1/SG1TB1/Projects/LigFEP_T4/COMPLETE_SETUP/FEP_SCHOLAR"
dest="/media/limn1/SG1TB1/Projects/T4-L99A_SuppInfo/EXP_default"

copy_job
untar_output
results

mv $dest/fep_scholar_$jobnum $dest/${dirname}_${conf}

