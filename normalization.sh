#!/bin/bash -l

# Necessary files and paths
DIR_OUT_NORM=/path/to/normalization_files/files
UNR_VCF=/path/to/unrelated.vcf
MATCHED_ID=/path/to/matched_id_200K_maf05

RANDOM_HAPLOID=/path/to/haploidize.py
ADNA_PATH="/path/to/adna_tools"; export ADNA_PATH

# Process unrelated VCF file
grep -e '#CHROM' ${UNR_VCF} > $DIR_OUT_NORM/unrelated.vcf
grep -w -f ${MATCHED_ID} ${UNR_VCF} >> $DIR_OUT_NORM/unrelated.vcf

# Haploidize randomly
python3 ${RANDOM_HAPLOID} $DIR_OUT_NORM/unrelated.vcf $DIR_OUT_NORM/unrelated_haploid.vcf

# Calculate dynamic kinship
python3 $ADNA_PATH/dynamic_kinship.py --vcf_file $DIR_OUT_NORM/unrelated_haploid.vcf --prefix $DIR_OUT_NORM/unr_wl200_ws50 --win_length 200 --win_shift 50

# Generate MSM baselines
for m in $(seq 1 22); do
  python3 $ADNA_PATH/msm_baseline.py --log_file $DIR_OUT_NORM/unr_wl200_ws50_${m}_MSM.log --prefix $DIR_OUT_NORM/msm_baseline_w200_ws50_${m} --mode mean
done

# Clean up intermediate files
rm $DIR_OUT_NORM/unr_wl*

# Downsample and process multiple VCFs
for N in 1000 1500 2000 2500 3000 3500 4000 4500 5000 6000 7000 8000 10000 12500 15000 20000 25000 30000 35000 40000 50000; do

  grep -e '#CHROM' $DIR_OUT_NORM/unrelated_haploid.vcf > $DIR_OUT_NORM/unrelated_${N}.vcf
  grep -v -e '#' $DIR_OUT_NORM/unrelated_haploid.vcf | shuf -n ${N} | sort -k1 -V >> $DIR_OUT_NORM/unrelated_${N}.vcf

  python3 $ADNA_PATH/dynamic_kinship.py --vcf_file $DIR_OUT_NORM/unrelated_${N}.vcf --prefix $DIR_OUT_NORM/unr_wl200_ws50_${N} --win_length 200 --win_shift 50

  rm $DIR_OUT_NORM/unrelated_${N}.vcf

  for m in $(seq 1 22); do
    python3 $ADNA_PATH/msm_baseline.py --log_file $DIR_OUT_NORM/unr_wl200_ws50_${N}_${m}_MSM.log --prefix $DIR_OUT_NORM/msm_baseline_wl200_ws50_${N}_${m} --mode mean
  done

done

# Final cleanup
rm $DIR_OUT_NORM/unr_wl*
