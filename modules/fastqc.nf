process FASTQC {

    input:
    path reads

    output:
    path "*.html"

    script:
    """
    fastqc $reads
    """
}
