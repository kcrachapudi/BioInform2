import subprocess
import os

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr)
    return result.stdout


def run_pipeline(fastq, reference="reference/reference.fa"):
    os.makedirs("results", exist_ok=True)

    # 1. Align
    run_command(f"bwa mem {reference} {fastq} > results/aligned.sam")

    # 2. Convert + sort
    run_command("samtools view -S -b results/aligned.sam > results/aligned.bam")
    run_command("samtools sort results/aligned.bam -o results/aligned_sorted.bam")
    run_command("samtools index results/aligned_sorted.bam")

    # 3. Variant calling
    run_command(
        f"bcftools mpileup -f {reference} results/aligned_sorted.bam | "
        "bcftools call -c -Ov -o results/variants.vcf"
    )

    return "results/variants.vcf"