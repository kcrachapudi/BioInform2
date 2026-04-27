import pandas as pd

def load_vcf(vcf_path):
    with open(vcf_path, "r") as f:
        lines = f.readlines()

    # remove metadata
    content = [l.strip() for l in lines if not l.startswith("##")]

    header = content[0].split("\t")
    data = [l.split("\t") for l in content[1:]]

    if not data:
        return pd.DataFrame(columns=header)

    df = pd.DataFrame(data, columns=header)

    # basic type fixes
    df["POS"] = df["POS"].astype(int)
    df["QUAL"] = pd.to_numeric(df["QUAL"], errors="coerce")

    return df


def summarize_vcf(df):
    if df.empty:
        return {
            "total_variants": 0,
            "message": "No variants detected"
        }

    snps = df[(df["REF"].str.len() == 1) & (df["ALT"].str.len() == 1)]
    indels = df[(df["REF"].str.len() != 1) | (df["ALT"].str.len() != 1)]

    return {
        "total_variants": len(df),
        "snps": len(snps),
        "indels": len(indels),
        "avg_quality": df["QUAL"].mean()
    }

import pandas as pd
import os

def parse_vcf(vcf_path):
    rows = []

    if not os.path.exists(vcf_path):
        # ❌ no Streamlit here
        return pd.DataFrame()

    with open(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                continue

            parts = line.strip().split("\t")

            if len(parts) < 8:
                continue

            try:
                chrom = parts[0]
                pos = int(parts[1])
                ref = parts[3]
                alt = parts[4]
                info = parts[7]

                # Clean ALT
                alt_alleles = alt.split(",")
                alt_alleles = [a for a in alt_alleles if a != "<*>"]

                if not alt_alleles:
                    continue

                alt = alt_alleles[0]

                # Extract depth
                dp = 0
                for field in info.split(";"):
                    if field.startswith("DP="):
                        dp = int(field.split("=")[1])

                # placeholder for now
                alt_freq = 1.0

                rows.append({
                    "CHROM": chrom,
                    "POS": pos,
                    "REF": ref,
                    "ALT": alt,
                    "DP": dp,
                    "ALT_FREQ": alt_freq
                })

            except Exception:
                continue

    return pd.DataFrame(rows)