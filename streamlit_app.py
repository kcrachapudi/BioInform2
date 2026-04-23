import streamlit as st
import os
from scripts.pipeline import run_pipeline, parse_vcf

st.set_page_config(page_title="BioInform2", layout="wide")

st.title("🧬 BioInform2: Variant Calling Pipeline")

# -------------------------
# Upload FASTQ
# -------------------------
uploaded_file = st.file_uploader("Upload FASTQ file", type=["fastq"])

if uploaded_file:
    os.makedirs("data", exist_ok=True)
    fastq_path = f"data/{uploaded_file.name}"

    with open(fastq_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"Uploaded: {uploaded_file.name}")

    # -------------------------
    # Run Pipeline
    # -------------------------
    if st.button("Run Pipeline"):
        with st.spinner("Running pipeline..."):
            vcf_path = run_pipeline(fastq_path)

        st.success("Pipeline complete!")

        # -------------------------
        # Load VCF
        # -------------------------
        if os.path.exists(vcf_path):
            df = parse_vcf(vcf_path)

            if df.empty:
                st.warning("No variants found.")
            else:
                st.subheader("Raw Variants")
                st.dataframe(df, use_container_width=True)

                # -------------------------
                # Simple Filtering UI
                # -------------------------
                st.subheader("Filter Variants")

                min_pos = int(df["POS"].min())
                max_pos = int(df["POS"].max())

                pos_range = st.slider(
                    "Position Range",
                    min_pos,
                    max_pos,
                    (min_pos, max_pos)
                )

                filtered_df = df[
                    (df["POS"] >= pos_range[0]) &
                    (df["POS"] <= pos_range[1])
                ]

                st.subheader("Filtered Variants")
                st.dataframe(filtered_df, use_container_width=True)

        else:
            st.error("VCF file not found.")