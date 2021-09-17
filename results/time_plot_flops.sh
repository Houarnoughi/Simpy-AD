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
		set title \"Task Execution Time\" offset 0,-0.8,0
		set terminal pdf enhanced color font 'Helvetica Bold,18'
        set output \"task_time_flops_para_pow.pdf\"
        set datafile separator \",\"
        set xlabel \"Tasks (Ordered by FLOP)\"
        set ylabel \"Execution Time (seconds)\"
        set yrange [0.01:*]
        set logscale y
        set format y \"10^{%T}\"
		set grid
		set key inside bottom left vertical box
		set key font 'Helvetica Bold,13'
		# set key width -4.5
		# set key spacing 0.6
        plot \"./$FILE1\" using 5:xticlabels(1) with lp ps 1 lw 2 ti \"Vehicle\" ,\
        \"./$FILE1\" using 6:xticlabels(1) with lp ps 1 lw 2 ti \"Fog\" ,\
        \"./$FILE1\" using 7:xticlabels(1) with lp ps 1 lw 2 ti \"Cloud\"" | gnuplot
