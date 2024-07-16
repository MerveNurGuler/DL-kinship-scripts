#!/bin/bash -l

# Set directories
DIR_PARENT=/path/to/PED_1st_deg
DIR_OUT_VCF=/path/to/final_files/analysis/wl200_ws50/vcfs
DIR_ASCMSM=/path/to/final_files/analysis/wl200_ws50

# Set paths to necessary scripts and files
RANDOM_HAPLOID=/path/to/haploidize.py
ADNA_PATH="/path/to/adna_tools"; export ADNA_PATH

# Enter the run directory
run=run_${1}
cd $DIR_PARENT
echo "Processing files in directory: ${run}"

cd ${run} || exit 1

# Process each VCF file
for file in parent-offspring_1.vcf parent-offspring_2.vcf siblings_1.vcf siblings_2.vcf siblings_3.vcf; do

  # Check if the file exists before processing
  if [ -e "$file" ]; then
    echo "Processing $file"

    vcfbase="${file%%.*}"  # Extract the base name without extension

    # Haploidize randomly
    python3 ${RANDOM_HAPLOID} $file $DIR_OUT_VCF/${run}_${vcfbase}_haploid.vcf
    
    # Calculate dynamic kinship
    python3 $ADNA_PATH/dynamic_kinship.py --vcf_file $DIR_OUT_VCF/${run}_${vcfbase}_haploid.vcf --prefix $DIR_ASCMSM/original/${run}_${vcfbase} --win_length 200 --win_shift 50

    # Downsample and process multiple VCFs
    for N in 1000 1500 2000 2500 3000 3500 4000 4500 5000 6000 7000 8000 10000 12500 15000 20000 25000 30000 35000 40000 50000
    do
      grep -e '#CHROM' $DIR_OUT_VCF/${run}_${vcfbase}_haploid.vcf > $DIR_OUT_VCF/${run}_${vcfbase}_${N}.vcf
      grep -v -e '#' $DIR_OUT_VCF/${run}_${vcfbase}_haploid.vcf | shuf -n ${N} | sort -k1 -V >> $DIR_OUT_VCF/${run}_${vcfbase}_${N}.vcf
      python3 $ADNA_PATH/dynamic_kinship.py --vcf_file $DIR_OUT_VCF/${run}_${vcfbase}_${N}.vcf --prefix $DIR_ASCMSM/downsample_${N}/${run}_${vcfbase} --win_length 200 --win_shift 50

      # Optionally remove intermediate files
      # rm $DIR_OUT_VCF/${run}_${vcfbase}_${N}.vcf
    done
  else
    echo "$file does not exist in $run"
  fi
done
