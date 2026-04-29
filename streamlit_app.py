import streamlit as st
import pandas as pd
import os

from dotenv import load_dotenv
load_dotenv()

from scripts.pipeline import run_pipeline
from scripts.vcf_parser import parse_vcf

CLOUD_MODE = os.getenv("CLOUD_MODE")

st.set_page_config(page_title="BioInform2", layout="wide")
st.title("🧬 BioInform2: Variant Calling Pipeline")

# ---------- INPUT ----------
st.subheader("Input Data")

use_sample = st.checkbox("Use sample data (recommended)", value=True)

uploaded_file = None
if not use_sample:
    uploaded_file = st.file_uploader("Upload FASTQ", type=["fastq"])

# ---------- INPUT INSPECTION ----------
st.subheader("Input Data (Raw)")

if use_sample:
    fastq_path = "data/sample.fastq"
    st.info(f"Using sample file: {fastq_path}")
else:
    if uploaded_file is not None:
        os.makedirs("data", exist_ok=True)
        fastq_path = "data/input.fastq"

        with open(fastq_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Uploaded file saved")
    else:
        fastq_path = None
        st.warning("No file uploaded")

# ---- SHOW RAW FASTQ ----
if fastq_path and os.path.exists(fastq_path):

    file_size = os.path.getsize(fastq_path)
    st.write(f"File size: {file_size} bytes")

    if file_size == 0:
        st.error("❌ File is EMPTY")
    else:
        with open(fastq_path) as f:
            lines = f.readlines()

        total_lines = len(lines)
        read_count = total_lines // 4

        st.write(f"Estimated Reads: {read_count}")

        # Preview
        st.write("Preview (first 3 reads):")
        st.text("".join(lines[:12]))

        # Structured view
        if read_count > 0:
            records = []
            for i in range(0, min(12, total_lines), 4):
                try:
                    records.append({
                        "ID": lines[i].strip(),
                        "SEQ": lines[i+1].strip(),
                        "QUAL": lines[i+3].strip()
                    })
                except IndexError:
                    continue

            st.write("Structured View:")
            st.dataframe(pd.DataFrame(records), width="stretch")

else:
    st.info("No input file available")

# ---------- RUN ----------
if st.button("Run Pipeline"):

    if CLOUD_MODE:
        st.info("Running in demo mode (precomputed VCF)")
        vcf_path = "results/variants.vcf"

    else:
        if not fastq_path:
            st.error("No FASTQ file available")
            st.stop()

        with st.spinner("Running pipeline..."):
            try:
                vcf_path = run_pipeline(fastq_path)
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                st.stop()

    # ---------- VCF PREVIEW ----------
    st.subheader("VCF Preview (Debug)")
    if os.path.exists(vcf_path):
        with open(vcf_path) as f:
            preview = "".join([next(f) for _ in range(15)])
        st.text(preview)
    else:
        st.error("VCF file not found!")
        st.stop()

    # ---------- PARSE ----------
    st.subheader("Parsing VCF...")
    df = parse_vcf(vcf_path)

    # ---------- STATUS ----------
    if df is None:
        st.error("❌ Parsing failed")
        df = pd.DataFrame()
    elif df.empty:
        st.warning("⚠️ 0 variants found")
    else:
        st.success(f"✅ {len(df)} variants found")

    # ---------- RAW GRID ----------
    st.subheader("Raw Parsed Data")
    st.dataframe(df, width="stretch")

    # ---------- FILTER ----------
    st.subheader("Filter Variants")

    if not df.empty and "POS" in df.columns:
        min_pos = int(df["POS"].min())
        max_pos = int(df["POS"].max())

        pos_range = st.slider(
            "Position Range",
            min_value=min_pos,
            max_value=max_pos,
            value=(min_pos, max_pos)
        )

        min_freq = st.slider(
            "Minimum ALT Frequency",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )

        filtered_df = df[
            (df["POS"] >= pos_range[0]) &
            (df["POS"] <= pos_range[1]) &
            (df["ALT_FREQ"] >= min_freq)
        ]
    else:
        st.warning("Skipping filters (no valid data)")
        filtered_df = pd.DataFrame()

    # ---------- FILTERED GRID ----------
    st.subheader("Filtered Variants")
    st.dataframe(filtered_df, width="stretch")

    # ---------- VISUALS ----------
    if not df.empty and "POS" in df.columns:
        st.subheader("Variant Distribution (Position)")
        st.bar_chart(df["POS"].value_counts().sort_index())

        if "ALT_FREQ" in df.columns:
            st.subheader("ALT Frequency Distribution")
            st.line_chart(df["ALT_FREQ"])
    else:
        st.info("No data available for visualization")

    # ---------- DOWNLOAD ----------
    st.subheader("Download Results")

    st.download_button(
        label="Download Filtered CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_variants.csv",
        mime="text/csv"
    )