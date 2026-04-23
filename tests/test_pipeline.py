from scripts.pipeline import run_pipeline
from scripts.vcf_parser import load_vcf, summarize_vcf

vcf_path = run_pipeline("data/real.fastq")

df = load_vcf(vcf_path)
summary = summarize_vcf(df)
print("Rows:", len(df))
print("Summary:", summary)