import pytest
import snakemake


def test_cgems_submission_end_to_end(tmp_path, qsub):
    with pytest.raises(SystemExit) as exc:
        args = [
            "-j",
            "1",
            "-s",
            "tests/data/job_scripts/basic.smk",
            "-d",
            tmp_path.as_posix(),
            "--profile",
            "src/cgr_gwas_qc/cluster_profiles/cgems",
        ]

        snakemake.main(args)

    assert exc.value.code == 0