#!/bin/bash

# Producing tree sequence files for chromosome 22
stdpopsim HomSap -c chr22 -o lbk_200_chr22.ts -g HapMapII_GRCh37 -d AncientEurasia_9K19 0 500

# Converting tree sequence files to VCF format
tskit vcf --ploidy 2 lbk_200_chr22.ts

# Remove headers from VCF files
sed -i -e '1,6d' lbk500_chr*.vcf

# Merge all chromosomes' VCFs
cat lbk500_chr{1..22}.vcf lbk500_chrX.vcf > lbk500.vcf

# Remove duplications
awk '!a[$1$2]++' lbk500.vcf > lbk500_nodup.vcf

# Create bed file from VCF positions
sed -e '1,6d' lbk500_nodup.vcf | awk '{print $1"\t"$2"\t"$2}' | awk '{$2=$2-1; print;}' | tr ' ' '\t' > bed.file

# Extract reference alleles
bedtools getfasta -fi /path/to/reference/genome/hs37d5.fa -bed bed.file -bedOut > ref_alleles

# Remove positions with allele 'N'
sed -i '/N/d' ref_alleles

# Prepare ID list for remaining positions
awk '{print $1"_"$3}' ref_alleles > ID_ref_alleles

# Merge chromosome and position columns to add ID column
awk '{$3=$1"_"$2; print;}' lbk500_nodup.vcf > lbk500_nodup_chrpos.vcf
sed -i -e '6s/#CHROM_POS/ID/' lbk500_nodup_chrpos.vcf

# Retaining positions according to the ID list
grep -w -f ID_ref_alleles lbk500_nodup_chrpos.vcf | cat | tr ' ' '\t' > lbk500_nodup_chrpos_noN.vcf

# Downsample VCF
sed -e '1,6d' lbk500_nodup_chrpos_noN.vcf | shuf -n 200000 | sort -V > lbk500_200K.vcf

# Create bed file for 200K SNP positions
awk '{print $1"\t"$2"\t"$2}' lbk500_200K.vcf | awk '{$2=$2-1; print;}' | tr ' ' '\t' > bed_200K.file

# Extract reference alleles for 200K SNPs
bedtools getfasta -fi /path/to/reference/genome/hs37d5.fa -bed bed_200K.file -bedOut > ref_alleles_200K

# Remove positions with allele 'N'
sed -i '/N/d' ref_alleles_200K

#Run the R script
Rscript nucleotide_integrating.R


