process BWA_INDEX {

    input:
    path ref

    output:
    path "reference.fa*"

    script:
    """
    bwa index $ref
    """
}
