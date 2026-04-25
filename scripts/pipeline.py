import subprocess
import os

RESULTS_DIR = "results"
LOGS_DIR = "logs"

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "pipeline.log")


def run_command(command):
    with open(LOG_FILE, "a") as log:
        log.write(f"\n[COMMAND] {command}\n")

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        log.write(result.stdout)
        log.write(result.stderr)

        if result.returncode != 0:
            raise Exception(result.stderr)

    return result.stdout


def index_reference(reference):
    if not os.path.exists(reference + ".bwt"):
        run_command(f"bwa index {reference}")


def run_alignment(fastq, reference):
    return run_command(
        f"bwa mem {reference} {fastq} > {RESULTS_DIR}/aligned.sam"
    )


def sam_to_bam():
    run_command(
        f"samtools view -S -b {RESULTS_DIR}/aligned.sam > {RESULTS_DIR}/aligned.bam"
    )


def sort_bam():
    run_command(
        f"samtools sort {RESULTS_DIR}/aligned.bam -o {RESULTS_DIR}/aligned_sorted.bam"
    )


def call_variants(reference):
    run_command(
        f"bcftools mpileup -f {reference} {RESULTS_DIR}/aligned_sorted.bam | "
        f"bcftools call -mv -Ov -o {RESULTS_DIR}/variants.vcf"
    )


def run_pipeline(fastq):
    reference = "reference/reference.fa"

    index_reference(reference)
    run_alignment(fastq, reference)
    sam_to_bam()
    sort_bam()
    call_variants(reference)

    return f"{RESULTS_DIR}/variants.vcf"