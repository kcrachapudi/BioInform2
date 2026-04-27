import subprocess
import os

RESULTS_DIR = "results"
LOGS_DIR = "logs"

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "pipeline.log")


def run_command(command_list, stdout_file=None):
    with open(LOG_FILE, "a") as log:
        log.write(f"\n[COMMAND] {' '.join(command_list)}\n")

        if stdout_file:
            with open(stdout_file, "w") as out:
                result = subprocess.run(
                    command_list,
                    stdout=out,
                    stderr=subprocess.PIPE,
                    text=True
                )
        else:
            result = subprocess.run(
                command_list,
                capture_output=True,
                text=True
            )

        log.write(result.stdout if result.stdout else "")
        log.write(result.stderr if result.stderr else "")

        if result.returncode != 0:
            raise Exception(result.stderr)

    return result.stdout


# ---------- STEPS ----------

def index_reference(reference):
    if not os.path.exists(reference + ".bwt"):
        run_command(["bwa", "index", reference])


def run_alignment(fastq, reference):
    sam_path = f"{RESULTS_DIR}/aligned.sam"

    run_command(
        ["bwa", "mem", reference, fastq],
        stdout_file=sam_path
    )

    return sam_path


def sam_to_bam():
    run_command([
        "samtools", "view",
        "-b",
        f"{RESULTS_DIR}/aligned.sam",
        "-o", f"{RESULTS_DIR}/aligned.bam"
    ])


def sort_bam():
    run_command([
        "samtools", "sort",
        f"{RESULTS_DIR}/aligned.bam",
        "-o", f"{RESULTS_DIR}/aligned_sorted.bam"
    ])


def index_bam():
    run_command([
        "samtools", "index",
        f"{RESULTS_DIR}/aligned_sorted.bam"
    ])


def call_variants(reference):
    # Use shell ONLY here for pipe
    command = (
        f"bcftools mpileup -f {reference} -d 1000 {RESULTS_DIR}/aligned_sorted.bam | "
        f"bcftools call -mv -Ov -o {RESULTS_DIR}/variants.vcf"
    )

    run_command(["bash", "-c", command])


# ---------- MAIN PIPELINE ----------

def run_pipeline(fastq):
    reference = "reference/reference.fa"

    index_reference(reference)
    run_alignment(fastq, reference)
    sam_to_bam()
    sort_bam()
    index_bam()
    call_variants(reference)

    return f"{RESULTS_DIR}/variants.vcf"


# ---------- CLI ENTRY ----------

if __name__ == "__main__":
    input_fastq = "data/real.fastq"  # change if needed
    vcf_path = run_pipeline(input_fastq)

    print(f"\n✅ Pipeline completed")
    print(f"📄 VCF generated at: {vcf_path}")