
setwd("/path/to/working/directory")

# Load reference and alternate alleles
ref_alt = read.table("tuscany_ref_alt")
colnames(ref_alt) <- c('REF','ALT')
ref_alt = ref_alt[-1,]

# Calculate transition and transversion probabilities
library(stringr)
A = as.data.frame(prop.table(table(as.factor(grep("^A",str_c(ref_alt$REF,'',ref_alt$ALT), value = TRUE)))))
G = as.data.frame(prop.table(table(as.factor(grep("^G",str_c(ref_alt$REF,'',ref_alt$ALT), value = TRUE)))))
C = as.data.frame(prop.table(table(as.factor(grep("^C",str_c(ref_alt$REF,'',ref_alt$ALT), value = TRUE)))))
T = as.data.frame(prop.table(table(as.factor(grep("^T",str_c(ref_alt$REF,'',ref_alt$ALT), value = TRUE)))))

ref_alleles = as.data.frame((read.table("ref_alleles_1M"))[,4])

new_nucleotides = data.frame(matrix(ncol = 2, nrow = nrow(ref_alleles)))
new_nucleotides[,1] = ref_alleles

for (i in 1:nrow(ref_alleles)) {
  if (new_nucleotides[i,1] == "A"){
    new_nucleotides[i,2] = substr(sample(A$Var1,1,prob = A$Freq),2,2)
  } 
  if (new_nucleotides[i,1] == "G"){
    new_nucleotides[i,2] = substr(sample(G$Var1,1,prob = G$Freq),2,2)
  } 
  if (new_nucleotides[i,1] == "C"){
    new_nucleotides[i,2] = substr(sample(C$Var1,1,prob = C$Freq),2,2)
  }
  if (new_nucleotides[i,1] == "T"){
    new_nucleotides[i,2] = substr(sample(T$Var1,1,prob = T$Freq),2,2)
  }
}

write.table(new_nucleotides, file="nuc_ref_alt_1M", quote = FALSE, row.names = FALSE, col.names = FALSE, sep = "\t")
