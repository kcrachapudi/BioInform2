import streamlit as st
import pandas as pd
import os

from dotenv import load_dotenv
load_dotenv()

from scripts.pipeline import run_pipeline

CLOUD_MODE = os.getenv("CLOUD_MODE")

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

    if not os.path.exists(vcf_path):
        st.error(f"VCF file not found: {vcf_path}")
        return pd.DataFrame()

    with open(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                continue

            parts = line.strip().split("\t")

            # 🔴 Safety check
            if len(parts) < 8:
                continue

            try:
                chrom = parts[0]
                pos = int(parts[1])
                ref = parts[3]
                alt = parts[4]
                info = parts[7]

                # Skip non-variant rows
                if alt == "." or alt == "<*>":
                    continue

                dp = 0
                alt_freq = 0

                for field in info.split(";"):
                    if field.startswith("DP="):
                        dp = int(field.split("=")[1])

                rows.append({
                    "CHROM": chrom,
                    "POS": pos,
                    "REF": ref,
                    "ALT": alt,
                    "DP": dp,
                    "ALT_FREQ": alt_freq
                })

            except Exception:
                # Skip bad lines safely
                continue

    return pd.DataFrame(rows)


# ---------- RUN ----------
if st.button("Run Pipeline"):

    if CLOUD_MODE:
        st.info("Running in demo mode (precomputed VCF)")
        vcf_path = "results/variants.vcf"

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

    # ---------- DEBUG ----------
    st.write("VCF Path:", vcf_path)

    # ---------- PARSE ----------
    df = parse_vcf(vcf_path)

    st.success("Pipeline completed!")

    # ---------- ALWAYS SHOW RAW ----------
    st.subheader("Raw Parsed Data (Debug View)")
    st.write("Shape:", df.shape)
    st.dataframe(df, width='stretch')

    # ---------- GUARD ----------
    if df.empty or "POS" not in df.columns:
        st.warning("No valid variants found or parsing failed.")
        st.stop()

    # ---------- ORIGINAL RAW GRID ----------
    st.subheader("Raw Variants")
    st.dataframe(df, width='stretch')

    # ---------- FILTER ----------
    st.subheader("Filter Variants")

    min_pos = int(df["POS"].min())
    max_pos = int(df["POS"].max())

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

    # ---------- FILTERED GRID ----------
    st.subheader("Filtered Variants")
    st.dataframe(filtered_df, width='stretch')

    # ---------- VISUALS ----------
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