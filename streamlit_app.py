import streamlit as st
import pandas as pd
import os

from scripts.pipeline import run_pipeline

CLOUD_MODE = True

st.title("🧬 BioInform2: Variant Calling Pipeline")

# ---------- INPUT ----------
st.subheader("Input Data")

use_sample = st.checkbox("Use sample data (recommended)", value=True)

uploaded_file = None
if not use_sample:
    uploaded_file = st.file_uploader("Upload FASTQ", type=["fastq"])

# ---------- VCF PARSER ----------
def parse_vcf(vcf_path):
    rows = []

    with open(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                continue

            parts = line.strip().split("\t")

            chrom = parts[0]
            pos = int(parts[1])
            ref = parts[3]
            alt = parts[4]
            info = parts[7]

            dp = 0
            dp4 = None

            for field in info.split(";"):
                if field.startswith("DP="):
                    dp = int(field.split("=")[1])
                if field.startswith("DP4="):
                    dp4 = list(map(int, field.split("=")[1].split(",")))

            alt_freq = 0
            if dp4:
                ref_count = dp4[0] + dp4[1]
                alt_count = dp4[2] + dp4[3]
                total = ref_count + alt_count

                if total > 0:
                    alt_freq = alt_count / total

            rows.append({
                "CHROM": chrom,
                "POS": pos,
                "REF": ref,
                "ALT": alt,
                "DP": dp,
                "ALT_FREQ": alt_freq
            })

    return pd.DataFrame(rows)

# ---------- RUN ----------
if st.button("Run Pipeline"):

    if CLOUD_MODE:
        st.info("Running in demo mode (precomputed VCF)")
        vcf_path = "results/demo_variants.vcf"

    else:
        if use_sample:
            fastq_path = "data/sample.fastq"
        else:
            if uploaded_file is None:
                st.error("Please upload a FASTQ file")
                st.stop()

            os.makedirs("data", exist_ok=True)
            fastq_path = "data/input.fastq"

            with open(fastq_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        vcf_path = run_pipeline(fastq_path)

    df = parse_vcf(vcf_path)

    st.success("Pipeline completed!")

    # ---------- RAW ----------
    st.subheader("Raw Variants")
    st.dataframe(df, use_container_width=True)

    # ---------- FILTER ----------
    st.subheader("Filter Variants")

    min_pos, max_pos = int(df["POS"].min()), int(df["POS"].max())

    pos_range = st.slider(
        "Position Range",
        min_pos,
        max_pos,
        (min_pos, max_pos)
    )

    min_freq = st.slider(
        "Minimum ALT Frequency",
        0.0,
        1.0,
        0.0,
        0.01
    )

    filtered_df = df[
        (df["POS"] >= pos_range[0]) &
        (df["POS"] <= pos_range[1]) &
        (df["ALT_FREQ"] >= min_freq)
    ]

    st.subheader("Filtered Variants")
    st.dataframe(filtered_df, use_container_width=True)

    # ---------- VISUAL ----------
    st.subheader("Variant Distribution")

    st.bar_chart(df["POS"].value_counts().sort_index())

    st.subheader("ALT Frequency Distribution")
    st.line_chart(df["ALT_FREQ"])

    # ---------- DOWNLOAD ----------
    st.download_button(
        "Download Filtered CSV",
        filtered_df.to_csv(index=False),
        "filtered_variants.csv"
    )


