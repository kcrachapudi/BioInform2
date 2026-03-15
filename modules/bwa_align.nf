process BWA_ALIGN {

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
