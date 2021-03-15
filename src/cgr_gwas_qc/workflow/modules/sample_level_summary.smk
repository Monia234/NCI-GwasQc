import pandas as pd


rule snp_qc_table:
    input:
        initial="sample_level/samples.lmiss",
        cr1="sample_level/call_rate_1/samples.lmiss",
        cr2="sample_level/call_rate_2/samples.lmiss",
        thousand_genomes="sample_level/call_rate_2/samples_1kg_rsID.csv",
    output:
        "sample_level/snp_qc.csv",
    script:
        "../scripts/snp_qc_table.py"


def _contam(wildcards):
    uf, wf = cfg.config.user_files, cfg.config.workflow_params
    if uf.idat_pattern and uf.gtc_pattern and wf.remove_contam:
        return "sample_level/contamination/verifyIDintensity_contamination.csv"
    return []


def _intensity(wildcards):
    uf, wf = cfg.config.user_files, cfg.config.workflow_params
    if uf.idat_pattern and uf.gtc_pattern and wf.remove_contam:
        return "sample_level/median_idat_intensity.csv"
    return []


rule sample_qc_report:
    input:
        imiss_start="sample_level/samples.imiss",
        imiss_cr1="sample_level/call_rate_1/samples.imiss",
        imiss_cr2="sample_level/call_rate_2/samples.imiss",
        sexcheck_cr1="sample_level/call_rate_1/samples.sexcheck",
        ancestry="sample_level/ancestry/graf_ancestry.txt",
        known_replicates="sample_level/concordance/KnownReplicates.csv",
        unknown_replicates="sample_level/concordance/UnknownReplicates.csv",
        contam=_contam,
        intensity=_intensity,
    output:
        all_samples="sample_level/qc_summary.csv",
    script:
        "../scripts/sample_qc_report.py"


rule sample_qc_report_summary_stats:
    input:
        rules.sample_qc_report.output.all_samples,
    output:
        "sample_level/qc_summary_stats.txt",
    script:
        "../scripts/sample_qc_report_summary_stats.py"


rule sample_lists_from_qc_flags:
    input:
        all_samples=rules.sample_qc_report.output.all_samples,
    output:
        cr="sample_level/qc_failures/low_call_rate.txt",
        contam="sample_level/qc_failures/contaminated.txt",
        sex="sample_level/qc_failures/sex_discordant.txt",
        rep="sample_level/qc_failures/replicate_discordant.txt",
        ctrl="sample_level/internal_controls.txt",
    script:
        "../scripts/sample_lists_from_qc_flags.py"


rule remove_contaminated:
    input:
        bed="{prefix}.bed",
        bim="{prefix}.bim",
        fam="{prefix}.fam",
        to_remove=rules.sample_lists_from_qc_flags.output.contam,
    params:
        out_prefix="{prefix}_contaminated_removed",
    output:
        bed="{prefix}_contaminated_removed.bed",
        bim="{prefix}_contaminated_removed.bim",
        fam="{prefix}_contaminated_removed.fam",
    log:
        "{prefix}_contaminated_removed.log",
    envmodules:
        cfg.envmodules("plink2"),
    conda:
        cfg.conda("plink2.yml")
    threads: lambda wildcards, attempt: attempt * 2
    resources:
        mem_mb=lambda wildcards, attempt: attempt * 1024,
    shell:
        "plink "
        "--bed {input.bed} "
        "--bim {input.bim} "
        "--fam {input.fam} "
        "--remove {input.to_remove} "
        "--make-bed "
        "--threads {threads} "
        "--memory {resources.mem_mb} "
        "--out {params.out_prefix}"