import os
import subprocess


# -------------------------------
# Core command runner
# -------------------------------
def run_command(cmd):
    print(f"\nRunning: {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print("ERROR:\n", result.stderr)
        raise Exception(result.stderr)

    return result.stdout


# -------------------------------
# Ensure BWA index exists
# -------------------------------
def ensure_bwa_index(reference):
    required_files = [
        reference + ".bwt",
        reference + ".sa",
        reference + ".ann",
        reference + ".pac",
    ]

    if not all(os.path.exists(f) for f in required_files):
        print("Indexing reference genome...")
        run_command(f"bwa index {reference}")
    else:
        print("BWA index already exists.")


# -------------------------------
# Alignment
# -------------------------------
def run_alignment(fastq, reference):
    return run_command(
        f"bwa mem {reference} {fastq} > results/aligned.sam"
    )


# -------------------------------
# SAM → BAM → Sorted + Indexed
# -------------------------------
def process_bam():
    run_command(
        "samtools view -S -b results/aligned.sam > results/aligned.bam"
    )

    run_command(
        "samtools sort results/aligned.bam -o results/aligned_sorted.bam"
    )

    run_command(
        "samtools index results/aligned_sorted.bam"
    )


# -------------------------------
# Variant Calling
# -------------------------------
def call_variants(reference):
    run_command(
        f"bcftools mpileup -f {reference} -Q 0 --min-MQ 0 results/aligned_sorted.bam | "
        "bcftools call -c -Ov -o results/variants.vcf"
    )

# -------------------------------
# Main Pipeline
# -------------------------------
def run_pipeline(fastq, reference="reference/reference.fa"):
    print("\n=== STARTING BIOINFORM PIPELINE ===\n")

    # create results folder
    os.makedirs("results", exist_ok=True)

    # step 1: index reference if needed
    ensure_bwa_index(reference)

    # step 2: alignment
    run_alignment(fastq, reference)

    # step 3: BAM processing
    process_bam()

    # step 4: variant calling
    call_variants(reference)

    print("\n=== PIPELINE COMPLETE ===\n")

    return "results/variants.vcf"

import pandas as pd

import pandas as pd


def parse_info_field(info_str):
    info_dict = {}
    for item in info_str.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            info_dict[key] = value
    return info_dict


def parse_vcf(vcf_path):
    rows = []

    with open(vcf_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue

            parts = line.strip().split("\t")

            chrom = parts[0]
            pos = int(parts[1])
            ref = parts[3]
            alt = parts[4]
            qual = parts[5]
            info = parts[7]

            info_dict = parse_info_field(info)

            # -------------------------
            # Extract DP4
            # -------------------------
            ref_count = 0
            alt_count = 0
            alt_freq = 0

            if "DP4" in info_dict:
                vals = list(map(int, info_dict["DP4"].split(",")))
                ref_count = vals[0] + vals[1]
                alt_count = vals[2] + vals[3]

                total = ref_count + alt_count
                if total > 0:
                    alt_freq = alt_count / total

            # -------------------------
            # Variant Type
            # -------------------------
            if len(ref) == 1 and len(alt) == 1:
                var_type = "SNP"
            else:
                var_type = "INDEL"

            rows.append({
                "CHROM": chrom,
                "POS": pos,
                "REF": ref,
                "ALT": alt,
                "QUAL": qual,
                "REF_COUNT": ref_count,
                "ALT_COUNT": alt_count,
                "ALT_FREQ": round(alt_freq, 3),
                "TYPE": var_type
            })

    return pd.DataFrame(rows)
    rows = []
    with open(vcf_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            rows.append({
                "CHROM": parts[0],
                "POS": int(parts[1]),
                "REF": parts[3],
                "ALT": parts[4],
                "QUAL": parts[5],
                "INFO": parts[7]
            })
    return pd.DataFrame(rows)