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

# Run the R script
Rscript nucleotide_integrating.R

# Merge new nucleotides with original VCF
paste lbk500_200K.vcf nuc_ref_alt_1M | awk '{print $1" "$2" "$3" "$260" "$261}' > lbk500_200K_part1.vcf
awk '{for(i=6;i<=NF;i++) printf $i" "; print ""}' lbk500_200K.vcf > lbk500_200K_part2.vcf
paste lbk500_200K_part1.vcf lbk500_1M_part2.vcf | tr ' ' '\t' > lbk500_wnuc_200K.vcf

# Add header
cat header lbk500_wnuc_200K.vcf | tr ' ' '\t' > lbk500_wnuc_200K_h.vcf

# Interpolation
ADNA_PATH=/path/to/adna_tools
python3 $ADNA_PATH/filter_vcf.py --vcf lbk500_wnuc_200K_h.vcf --prefix inter_biSNPs_lbk_200K --f_maps /path/to/genetic_map/female_chr{}.txt --m_maps /path/to/genetic_map/male_chr{}.txt --x_chr X --interpolate

mv lbk500_wnuc_200K_h.vcf founders_200K.vcf

# Remove the header except for column names
awk 'NR==1 {print; exit}' founders_200K.vcf > firstline

# Create a new header with assigned sexes
Rscript -e "
setwd('/path/to/working/directory')
header = read.csv2('firstline', sep='\t', header=FALSE, stringsAsFactors = FALSE)
library(stringr)
header = str_replace_all(header, 'tsk_', 'ind')
a = sample(x = c('M', 'F'), prob = c(.5, .5), size = 250, replace = TRUE)
fam_file = data.frame(matrix(ncol = 2, nrow = 250))
newheader = header
for (i in 10:259) {
  newheader[i] = str_c(header[i],'',a[(i-9)])
  fam_file[(i-9),1] = newheader[i]
  fam_file[(i-9),2] = a[(i-9)]
}
write.table(fam_file, file='founders_1M.fam', quote = FALSE, row.names = FALSE, col.names = FALSE, sep = '\t')
write.table(t(as.data.frame(newheader)), file='header_wsex', quote = FALSE, row.names = FALSE, col.names = FALSE, sep = '\t')
"

# Combine header with VCF
cat header_wsex founders_200K.vcf | sed -e '2d' > founders_200K_final.vcf

