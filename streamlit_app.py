import streamlit as st
import os
import pandas as pd

from scripts.pipeline import run_pipeline, parse_vcf

st.set_page_config(page_title="BioInform2", layout="wide")

st.title("🧬 BioInform2: Variant Calling Pipeline")

# =========================
# INPUT MODE
# =========================
mode = st.radio(
    "Select Input Source",
    ["Use Sample Data", "Upload FASTQ"]
)

fastq_path = None

# -------------------------
# SAMPLE MODE
# -------------------------
if mode == "Use Sample Data":
    fastq_path = "data/sample.fastq"
    st.info("Using built-in sample dataset")

# -------------------------
# UPLOAD MODE
# -------------------------
elif mode == "Upload FASTQ":
    uploaded_file = st.file_uploader("Upload FASTQ file", type=["fastq"])

    if uploaded_file:
        os.makedirs("data", exist_ok=True)
        fastq_path = f"data/{uploaded_file.name}"

        with open(fastq_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"Uploaded: {uploaded_file.name}")

# =========================
# RUN PIPELINE
# =========================
if fastq_path:

    run = st.button("Run Pipeline") if mode == "Upload FASTQ" else True

    if run:
        with st.spinner("Running pipeline..."):
            vcf_path = run_pipeline(fastq_path)

        st.success("Pipeline complete!")

        if os.path.exists(vcf_path):

            df = parse_vcf(vcf_path)

            if df.empty:
                st.warning("No variants found.")
            else:

                # =========================
                # ORIGINAL: RAW GRID
                # =========================
                st.subheader("Raw Variants Data")
                def highlight_variants(row):
                    if row["ALT_FREQ"] >= highlight_threshold:
                        return ["background-color: #ffcccc"] * len(row)  # light red
                    return [""] * len(row)

                highlight_threshold = st.slider(
                    "Highlight Threshold (ALT Frequency)",
                    0.0, 1.0, 0.5, 0.05
                )

                styled_df = df.style.apply(highlight_variants, axis=1)

                st.dataframe(styled_df, use_container_width=True)
                # =========================
                # NEW: VISUALIZATION
                # =========================
                st.subheader("Allele Frequency Distribution")

                bins = {
                    "0.0-0.2": 0,
                    "0.2-0.4": 0,
                    "0.4-0.6": 0,
                    "0.6-0.8": 0,
                    "0.8-1.0": 0
                }

                for val in df["ALT_FREQ"]:
                    if val <= 0.2:
                        bins["0.0-0.2"] += 1
                    elif val <= 0.4:
                        bins["0.2-0.4"] += 1
                    elif val <= 0.6:
                        bins["0.4-0.6"] += 1
                    elif val <= 0.8:
                        bins["0.6-0.8"] += 1
                    else:
                        bins["0.8-1.0"] += 1

                chart_data = pd.DataFrame([
                    {"Range": k, "Count": v} for k, v in bins.items()
                ])

                st.bar_chart(chart_data.set_index("Range"))

                st.subheader("Variant Positions (ALT Frequency)")
                st.line_chart(df.set_index("POS")["ALT_FREQ"])

                # =========================
                # ORIGINAL: FILTER CONTROLS
                # =========================
                st.subheader("Filter Variants")

                col1, col2 = st.columns(2)

                with col1:
                    pos_range = st.slider(
                        "Position Range",
                        int(df["POS"].min()),
                        int(df["POS"].max()),
                        (int(df["POS"].min()), int(df["POS"].max()))
                    )

                with col2:
                    min_alt_freq = st.slider(
                        "Minimum ALT Frequency",
                        0.0,
                        1.0,
                        0.0,
                        0.05
                    )

                filtered_df = df[
                    (df["POS"] >= pos_range[0]) &
                    (df["POS"] <= pos_range[1]) &
                    (df["ALT_FREQ"] >= min_alt_freq)
                ]

                # =========================
                # ORIGINAL: FILTERED GRID
                # =========================
                st.subheader("Filtered Variants Data")
                styled_filtered_df = filtered_df.style.apply(highlight_variants, axis=1)

                st.dataframe(styled_filtered_df, use_container_width=True)
                # =========================
                # NEW: DOWNLOAD
                # =========================
                st.subheader("Download Results")

                csv = filtered_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download Filtered Variants (CSV)",
                    data=csv,
                    file_name="filtered_variants.csv",
                    mime="text/csv"
                )

        else:
            st.error("VCF file not found.")