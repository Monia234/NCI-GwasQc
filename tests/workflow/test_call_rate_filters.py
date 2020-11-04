from pathlib import Path
from shutil import copytree
from subprocess import run
from textwrap import dedent

import pytest

from cgr_gwas_qc import load_config
from cgr_gwas_qc.testing import chdir


def test_call_rate_config(gtc_working_dir):
    """Make sure config options are the correct floats."""
    with chdir(gtc_working_dir):
        cfg = load_config()
        assert cfg.config.software_params.samp_cr_1 == 0.8
        assert cfg.config.software_params.samp_cr_2 == 0.95


@pytest.mark.workflow
def test_call_rate_filter1(tmp_path: Path, gtc_working_dir: Path):
    copytree(gtc_working_dir, tmp_path, dirs_exist_ok=True)
    snake = tmp_path / "Snakefile"
    snake.write_text(
        dedent(
            """\
    from cgr_gwas_qc import load_config

    cfg = load_config()

    include: cfg.rules("entry_points.smk")
    include: cfg.rules("call_rate_filters.smk")

    rule all:
        input:
            expand("plink_filter_call_rate_1/samples.{ext}", ext=["bed", "bim", "fam"])
    """
        )
    )

    with chdir(tmp_path):
        run(["snakemake", "-j1", "--use-conda", "--nocolor"], check=True)
        assert Path("plink_filter_call_rate_1/samples.bed").exists()
        assert Path("plink_filter_call_rate_1/samples.bim").exists()
        assert Path("plink_filter_call_rate_1/samples.fam").exists()


@pytest.mark.workflow
def test_call_rate_filter2(tmp_path: Path, gtc_working_dir: Path):
    copytree(gtc_working_dir, tmp_path, dirs_exist_ok=True)
    snake = tmp_path / "Snakefile"
    snake.write_text(
        dedent(
            """\
    from cgr_gwas_qc import load_config

    cfg = load_config()

    include: cfg.rules("entry_points.smk")
    include: cfg.rules("call_rate_filters.smk")

    rule all:
        input:
            expand("plink_filter_call_rate_2/samples.{ext}", ext=["bed", "bim", "fam"])
    """
        )
    )

    with chdir(tmp_path):
        run(["snakemake", "-j1", "--use-conda", "--nocolor"], check=True)
        assert Path("plink_filter_call_rate_2/samples.bed").exists()
        assert Path("plink_filter_call_rate_2/samples.bim").exists()
        assert Path("plink_filter_call_rate_2/samples.fam").exists()
