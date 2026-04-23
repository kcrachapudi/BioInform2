from scripts.pipeline import run_pipeline
from scripts.vcf_parser import load_vcf

vcf_path = run_pipeline("data/sample.fastq")

df = load_vcf(vcf_path)

print("Rows:", len(df))
print(df.head())