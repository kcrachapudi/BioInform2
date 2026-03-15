#!/usr/bin/env nextflow

include { FASTQC } from './modules/fastqc'
include { BWA_INDEX } from './modules/bwa_index'
include { BWA_ALIGN } from './modules/bwa_align'

params.reads = "data/sample.fastq"
params.ref   = "reference/reference.fa"

workflow {

    reads = file(params.reads)
    ref   = file(params.ref)

    indexed_ref = BWA_INDEX(ref)

    FASTQC(reads)

    BWA_ALIGN(reads, indexed_ref)
}
