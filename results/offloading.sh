#!/bin/sh

if [ $# -lt 1 ]; then
  echo "Usage :"$0" <csv_file>"
  exit 1
fi

FILE1=$1

if [ ! -e $FILE ]; then
  echo "Error: $1 does not exist"
  exit 1
fi

# Define bounds
#~ t_max=$(awk -F ";" '{ print $1 }' $FILE | sort -n | sed -n '$p')
#~ p_max=$(( $(awk -F ";" '{ print $2 }' $FILE | sort -n | sed -n '$p') + 5 ))
#~ p_min=$(( $(awk -F ";" '{ print $2 }' $FILE | sort -n | sed -n '1p') - 5 ))

# The output file name
OUT=$(echo $FILE | awk -F "." '{print $1}').eps

echo "
		clear
		reset
		unset key
		set encoding iso_8859_1
		set title \"Method with knowledge sharing\" offset 0,-0.8,0
		set terminal pdf enhanced color font 'Helvetica Bold,18'
        set output \"without_sharing.pdf\"
        set datafile separator \",\"
        set xlabel \"Simulation steps\"
        set ylabel \"Rate of accepted offloading\"
        set yrange [0:*]
		set format y \"%g %%\"
		set grid
		set key inside top right vertical box
		set key font 'Helvetica Bold,13'
		# set key width -4.5
		# set key spacing 0.6
        plot \"./$FILE1\" using 2:xticlabels(1) with lp ps 1 lw 2 ti \"Agent 1\" ,\
        \"./$FILE1\" using 3:xticlabels(1) with lp ps 1 lw 2 ti \"Agent 2\" ,\
        \"./$FILE1\" using 4:xticlabels(1) with lp ps 1 lw 2 ti \"Agent 3 \" ,\
        \"./$FILE1\" using 5:xticlabels(1) with lp ps 1 lw 2 ti \"Agent 4\" ,\
        \"./$FILE1\" using 6:xticlabels(1) with lp ps 1 lw 2 ti \"Agent 5\" " | gnuplot
