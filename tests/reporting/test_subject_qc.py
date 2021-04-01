import shutil
from pathlib import Path
from typing import Tuple

import pytest

# real_config, sample_sheet_full, sample_qc_df, population_qc_df


@pytest.mark.real_data
def test_Relatedness(population_qc_df):
    from cgr_gwas_qc.reporting.subject_qc import Relatedness

    rl = Relatedness.construct(population_qc_df)

    assert 0 == rl.num_related_subjects
    assert 0 == rl.num_qc_families


@pytest.fixture(params=[1, 2, 5])
def num_and_png_dir(request, tmp_path, fake_image) -> Tuple[int, Path]:
    for i in range(request.param):
        shutil.copy(fake_image, tmp_path / f"Pop{i}.png")

    return request.param, tmp_path


@pytest.mark.real_data
def test_Autosomal(population_qc_df, num_and_png_dir):
    from cgr_gwas_qc.reporting.subject_qc import Autosomal

    num_pops, png_dir = num_and_png_dir
    az = Autosomal.construct(population_qc_df, png_dir)

    assert 1 == az.num_populations_analyzed
    assert 0 == az.num_subjects_excluded
    assert num_pops == len(az.panels)


def test_Pca(num_and_png_dir):
    from cgr_gwas_qc.reporting.subject_qc import Pca

    num_pops, png_dir = num_and_png_dir
    pca = Pca.construct(png_dir)

    assert num_pops == len(pca.panels)


def test_Hwe(num_and_png_dir):
    from cgr_gwas_qc.reporting.subject_qc import Hwe

    num_pops, png_dir = num_and_png_dir
    hwe = Hwe.construct(png_dir)

    assert num_pops == len(hwe.panels)