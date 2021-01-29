import pandas as pd
from more_itertools import flatten


################################################################################
# Population Level Analysis
#   - PCA
#   - Autosomal Heterozygosity
#   - IBS/IBD
################################################################################
rule subjects_per_population:
    input:
        "sample_level/qc_summary.csv",
    output:
        "population_level/{population}/subject_list.txt",
    run:
        # TODO: Exclude subjects that are unexpected reps (issue #44)
        (
            pd.read_csv(input[0])
            .query("Subject_Representative & Ancestry == @wildcards.population")
            .assign(Subject_ID2=lambda x: x.Group_By_Subject_ID)
            .reindex(["Group_By_Subject_ID", "Subject_ID2"], axis=1)
            .to_csv(output[0], sep=" ", index=False, header=False)
        )


rule plink_split_population:
    input:
        bed="subject_level/subjects.bed",
        bim="subject_level/subjects.bim",
        fam="subject_level/subjects.fam",
        to_keep=rules.subjects_per_population.output[0],
    params:
        out_prefix="population_level/{population}/subjects",
    output:
        bed="population_level/{population}/subjects.bed",
        bim="population_level/{population}/subjects.bim",
        fam="population_level/{population}/subjects.fam",
        nosex="population_level/{population}/subjects.nosex",
    log:
        "population_level/{population}/subjects.log",
    wildcard_constraints:
        population="\w+",
    envmodules:
        cfg.envmodules("plink2"),
    conda:
        cfg.conda("plink2.yml")
    threads: 20
    resources:
        mem=10000,
    shell:
        "plink "
        "--bed {input.bed} "
        "--bim {input.bim} "
        "--fam {input.fam} "
        "--keep {input.to_keep} "
        "--make-bed "
        "--threads {threads} "
        "--memory {resources.mem} "
        "--out {params.out_prefix}"


def required_population_results(wildcards):
    """Decide what populations to analyze.

    If a population has fewer than `workflow_params.minimum_pop_subjects`
    subjects than ignore.
    """
    qc_table = checkpoints.sample_qc_report.get(**wildcards).output[0]

    maf = cfg.config.software_params.maf_for_ibd
    ld = cfg.config.software_params.ld_prune_r2
    population_threshold = cfg.config.workflow_params.minimum_pop_subjects

    pops = (
        pd.read_csv(qc_table)
        .query("Subject_Representative")
        .groupby("Ancestry")
        .size()
        .pipe(lambda x: x[x > population_threshold])
        .index.values.tolist()
    )

    return flatten(
        [
            expand(
                "population_level/{population}/subjects_maf{maf}_ld{ld}_pruned.eigenvec",
                population=pops,
                maf=maf,
                ld=ld,
            ),  # PCA
            expand(
                "population_level/{population}/subjects_maf{maf}_ld{ld}_pruned.genome",
                population=pops,
                maf=maf,
                ld=ld,
            ),  # IBS/IBD
            expand(
                "population_level/{population}/subjects.het", population=pops, maf=maf, ld=ld,
            ),  # Autosomal Heterozygosity
        ]
    )


rule phony_population_results:
    input:
        required_population_results,
    output:
        "population_level/results.done",
    shell:
        "echo {input} | xargs printf '%s\n' > {output[0]}"


################################################################################
# Population Level Analysis (Controls Only)
#   - HWE
################################################################################
rule controls_per_population:
    input:
        "sample_level/qc_summary.csv",
    output:
        "population_level/{population}/controls_list.txt",
    run:
        # TODO: Exclude subjects that are unexpected reps (issue #44)
        (
            pd.read_csv(input[0])
            .query(
                "Subject_Representative & Ancestry == @wildcards.population & `Case/Control_Status` == 0"
            )
            .assign(Subject_ID2=lambda x: x.Group_By_Subject_ID)
            .reindex(["Group_By_Subject_ID", "Subject_ID2"], axis=1)
            .to_csv(output[0], sep=" ", index=False, header=False)
        )


rule plink_split_controls:
    input:
        bed=rules.plink_split_population.output.bed,
        bim=rules.plink_split_population.output.bim,
        fam=rules.plink_split_population.output.fam,
        to_keep=rules.controls_per_population.output[0],
    params:
        out_prefix="population_level/{population}/controls",
    output:
        bed="population_level/{population}/controls.bed",
        bim="population_level/{population}/controls.bim",
        fam="population_level/{population}/controls.fam",
        nosex="population_level/{population}/controls.nosex",
    log:
        "population_level/{population}/controls.log",
    envmodules:
        cfg.envmodules("plink2"),
    conda:
        cfg.conda("plink2.yml")
    threads: 20
    resources:
        mem=10000,
    shell:
        "plink "
        "--bed {input.bed} "
        "--bim {input.bim} "
        "--fam {input.fam} "
        "--keep {input.to_keep} "
        "--make-bed "
        "--threads {threads} "
        "--memory {resources.mem} "
        "--out {params.out_prefix}"


def required_population_controls(wildcards):
    """Decide what populations controls to analyze.

    If population controls have fewer than `workflow_params.control_hwp_threshold`
    subjects than ignore.
    """
    qc_table = checkpoints.sample_qc_report.get(**wildcards).output[0]

    maf = cfg.config.software_params.maf_for_hwe
    control_threshold = cfg.config.workflow_params.control_hwp_threshold

    pops = (
        pd.read_csv(qc_table)
        .query("Subject_Representative & `Case/Control_Status` == 0")
        .groupby("Ancestry")
        .size()
        .pipe(lambda x: x[x > control_threshold])
        .index.values.tolist()
    )

    return expand(
        "population_level/{population}/controls_maf{maf}_snps_autosome_cleaned.hwe",
        population=pops,
        maf=maf,
    )  # HWE


rule phony_population_controls:
    input:
        required_population_controls,
    output:
        "population_level/controls.done",
    shell:
        "echo {input} | xargs printf '%s\n' > {output[0]}"