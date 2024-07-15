#!/bin/bash

PEDSIM_PATH=/path/to/ped-sim
VCF_PATH=/path/to/founders_200k_final.vcf
MAP_PATH=/path/to/inter_biSNPs_lbk_200K.map
SEX_PATH=/path/to/founders_200K.fam
INTF_PATH=$PEDSIM_PATH/interfere/nu_p_campbell_X.tsv

first=1
last=60

for ((i=$first; i <= $last; i++))
do
  echo "RUN $i of $last"
  mkdir run_$i
  for ((j=1; j <= 4; j++))
  do
    $PEDSIM_PATH/ped-sim -d /path/to/def/grandparent-grandchild_$j.def -m $MAP_PATH -o ./run_$i/grandparent-grandchild_$j -i $VCF_PATH -X X --intf $INTF_PATH --sexes $SEX_PATH --keep_phase --founder_ids --fam --miss_rate 0
  done
  for ((j=1; j <= 8; j++))
  do
    $PEDSIM_PATH/ped-sim -d /path/to/def/avuncular_$j.def -m $MAP_PATH -o ./run_$i/avuncular_$j -i $VCF_PATH -X X --intf $INTF_PATH --sexes $SEX_PATH --keep_phase --founder_ids --fam --miss_rate 0
  done
  for ((j=1; j <= 6; j++))
  do
    $PEDSIM_PATH/ped-sim -d /path/to/def/half-siblings_$j.def -m $MAP_PATH -o ./run_$i/half-siblings_$j -i $VCF_PATH -X X --intf $INTF_PATH --sexes $SEX_PATH --keep_phase --founder_ids --fam --miss_rate 0
  done
done
