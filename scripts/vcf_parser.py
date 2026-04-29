import pandas as pd


def parse_vcf(vcf_path):
    rows = []

    with open(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                continue

            parts = line.strip().split("\t")

            if len(parts) < 8:
                continue

            rows.append({
                "CHROM": parts[0],
                "POS": int(parts[1]),
                "REF": parts[3],
                "ALT": parts[4],
                "INFO": parts[7]
            })

    return pd.DataFrame(rows)