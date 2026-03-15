#!/usr/bin/env nextflow

params.reads = "data/sample.fastq"
params.ref   = "reference/reference.fa"

process index_ref {

    input:
    path ref

    output:
    path "reference.fa*"

    script:
    """
    bwa index $ref
    """
}

process fastqc {

    input:
    path reads

    output:
    path "*.html"

    script:
    """
    fastqc $reads
    """
}

process align {

    input:
    path reads
    path ref_index

    output:
    path "aligned.sam"

    script:
    """
    bwa mem reference.fa $reads > aligned.sam
    """
}

workflow {

    reads = file(params.reads)
    ref   = file(params.ref)

    indexed_ref = index_ref(ref)

    fastqc(reads)

    align(reads, indexed_ref)
}
