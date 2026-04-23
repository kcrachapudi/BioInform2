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