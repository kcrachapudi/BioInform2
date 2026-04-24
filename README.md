🧬 BioInform2 — Variant Calling & Analysis Pipeline
📌 Overview
BioInform2 is an end-to-end Next Generation Sequencing (NGS) variant calling pipeline built using Python and exposed through an interactive Streamlit interface.
The project demonstrates how raw sequencing reads (FASTQ) are transformed into biologically meaningful insights (genetic variants) through alignment, variant calling, parsing, and visualization.
This project emphasizes:


Reproducible bioinformatics workflows


Separation of concerns (pipeline vs UI)


Interpretability of VCF data


Interactive data exploration



🧪 Problem Statement
Raw sequencing data is noisy and unstructured. Extracting meaningful genetic variation requires:


Aligning reads to a reference genome


Identifying differences (variants)


Filtering noise from true biological signals


Interpreting results in a usable format


Most pipelines are:


CLI-heavy


Hard to interpret


Not user-friendly


👉 BioInform2 solves this by combining pipeline automation + interactive analytics.

🏗️ Pipeline Architecture
FASTQ → Alignment → BAM → Variant Calling → VCF → Parsing → Analysis → Visualization
🔬 Step-by-step
1. Input (FASTQ)


Raw sequencing reads


Format: nucleotide sequences + quality scores


2. Reference Genome


Provided FASTA file (reference/reference.fa)


Used as baseline for alignment



⚙️ 3. Alignment (BWA)
Tool: bwa mem
What happens technically:


Uses Burrows-Wheeler Transform (BWT) for fast lookup


Maps reads to reference positions


Produces SAM (Sequence Alignment Map)


Scientific meaning:


Determines where each read belongs in the genome



📦 4. SAM → BAM → Sorting
Tool: samtools
Steps:


Convert SAM → BAM (binary format)


Sort reads by genomic position


Prepare for variant calling


Why:


Efficient storage


Required for downstream tools



🧬 5. Variant Calling (bcftools)
Tools:


bcftools mpileup


bcftools call


Technical:


Aggregates read evidence at each genomic position


Computes:


Depth (DP)


Base counts


Quality metrics




Identifies differences vs reference


Output:


VCF (Variant Call Format)



📄 Understanding VCF
Each row represents a genomic position:
FieldMeaningCHROMChromosomePOSPositionREFReference baseALTAlternate baseINFOMetrics (depth, bias, etc.)

🧠 Key Metrics Used
DP (Depth)


Total reads covering position


DP4
Breakdown:
ref-forward, ref-reverse, alt-forward, alt-reverse
👉 Used to compute:
ALT_FREQ (derived)
ALT_FREQ = (alt_forward + alt_reverse) / total_depth
Scientific interpretation:


~1.0 → strong mutation signal


~0.5 → heterozygous-like signal


~0.0 → no mutation



🧠 Python Pipeline Design
The pipeline is fully Python-driven (no bash scripts):
Core file:
scripts/pipeline.py
Responsibilities:


Run external tools (BWA, samtools, bcftools)


Manage file flow


Parse VCF into structured DataFrame



🧩 Separation of Concerns
LayerResponsibilitypipeline.pyData processingstreamlit_app.pyUI + interactiondata/Input filesresults/Outputs

📊 Streamlit Application
Interactive UI for running and analyzing the pipeline.

🔹 Features
1. Input Options


✅ Use sample dataset


✅ Upload custom FASTQ



2. Pipeline Execution


One-click run


Real-time status feedback



3. Raw Variant Data


Full VCF parsed into table


Columns:


Position


REF / ALT


Depth


ALT Frequency





4. Visualization
Allele Frequency Distribution


Histogram of mutation strength


Variant Position Plot


Shows where mutations occur along genome



5. Filtering
Interactive controls:


Position range


Minimum ALT frequency


👉 Enables isolation of high-confidence variants

6. Highlighting (Interpretation Layer)


Variants with high ALT_FREQ visually emphasized


Helps identify biologically meaningful mutations quickly



7. Export


Download filtered variants as CSV



📁 Project Structure
BioInform2/│├── data/│   └── sample.fastq│├── reference/│   └── reference.fa│├── results/│   ├── aligned.sam│   ├── aligned_sorted.bam│   └── variants.vcf│├── scripts/│   └── pipeline.py│├── tests/│   └── test_pipeline.py│├── streamlit_app.py└── README.md

🚀 How to Run
1. Setup environment
python -m venv venvsource venv/bin/activate  # or Windows equivalentpip install streamlit pandas

2. Install tools
Ensure installed:


bwa


samtools


bcftools



3. Run Streamlit app
streamlit run streamlit_app.py

🧪 Example Output


~48 variant positions (sample dataset)


ALT frequency distribution visualized


Filtering reduces noise → isolates true variants



🧠 What This Project Demonstrates
Technical Skills


Python pipeline orchestration


External tool integration


Data parsing (VCF → DataFrame)


Streamlit app development


Debugging bioinformatics workflows



Bioinformatics Knowledge


NGS data flow


Read alignment concepts


Variant calling logic


Interpretation of sequencing metrics


Noise vs true signal distinction



⚠️ Limitations


Uses simplified reference genome


No annotation (genes, clinical relevance)


Single-sample pipeline


No parallelization



🔮 Future Enhancements


Variant annotation (ClinVar, gene mapping)


Multi-sample comparison


Cloud execution (GCP / AWS)


Scalable workflow orchestration


Integration with genome browsers (IGV)



🎯 Why This Matters
This project bridges:
👉 Raw sequencing data → actionable biological insight
It reflects real-world workflows used in:


Genomics research


Clinical diagnostics


Precision medicine



👨‍💻 Author Notes
This project is part of a structured Bioinformatics portfolio series (BioInform1–4), progressively building:


QC & preprocessing


Variant calling (this project)


Scalable workflows


Advanced analysis



If you want, next we can:


tighten this to a resume bullet version


or upgrade this into a GitHub portfolio showcase (with badges + visuals)

