"""Cache conda environments for faster testing.

Testing was slowed down b/c each test, that used a snakemake rule with a
conda environment, had to build that conda environment. This was not too bad
at first b/c environments are pretty small. However, the illuminaio
environment was taking a long time.

This module builds all conda environments in the
``src/cgr_gwas_qc/workflow/conda`` folder and stores them in a cache folder
(the default location is ``GwasQcPipeline/.cache/cgr_gwas_qc/conda`` but can
be changed by setting ``XDG_CACHE_HOME``).

Then the ``copy_env()`` method is used to copy conda environments into the
testing directory.
"""
import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Union


class CondaEnv:

    conda_env_path = Path(__file__).absolute().parents[1] / "workflow/conda"

    def __init__(self, cache_path: Optional[Union[str, Path]] = None):
        self._cache_path = self._make_cache(cache_path)
        self._build_conda_envs()

    def _make_cache(self, user_path: Optional[Union[str, Path]]) -> Path:
        """Create cache folder."""
        suffix = "cgr_gwas_qc/conda"

        if user_path:
            _cache_path = Path(user_path) / suffix
        elif os.environ.get("XDG_CACHE_HOME"):
            _cache_path = Path(os.environ["XDG_CACHE_HOME"]) / suffix
        else:
            _cache_path = Path(__file__).absolute().parents[3] / ".cache" / suffix

        _cache_path.mkdir(parents=True, exist_ok=True)
        return _cache_path

    def _build_conda_envs(self) -> None:
        """Build all conda envs.

        Iterate over conda envs in ``src/cgr_gwas_qc/workflow/conda`` and
        build them all into a cache directory.
        """
        for env in self.conda_env_path.glob("*.yml"):
            build_path = self._get_env_cache_path(env)

            if build_path.exists():
                continue

            self._create_conda_env(env.as_posix(), build_path.as_posix())

    def _get_env_cache_path(self, env: Path) -> Path:
        """Create cache path name based on env content.

        Uses md5sum of the environment YAML file to create a path name in the
        form of ``{env name}_{yaml hash}``.
        """
        md5 = hashlib.md5()
        md5.update(env.read_bytes())
        content_hash = md5.hexdigest()[:8]
        return self._cache_path / f"{env.stem}_{content_hash}"

    def _create_conda_env(self, env_file: str, build_path: str) -> None:
        """Create the conda environment.

        Uses conda (or mamba if present) to build the conda environment in
        the build path.
        """
        conda_frontend = "mamba" if shutil.which("mamba") else "conda"
        cmd = " ".join(
            [
                conda_frontend,
                "env",
                "create",
                "--quiet",
                "--file",
                env_file,
                "--prefix",
                build_path,
            ]
        )
        subprocess.run(cmd, shell=True, check=True, stderr=subprocess.STDOUT)

    def _get_working_dir_env_path(self, env: Path, working_dir: Path) -> Path:
        """Working directory env path.

        For snakemake, the environment path should be the md5sum of the full
        path to `{working_dir}/.snakemake/conda` as well as the content of
        the YAML file. Snakemake uses the first 8 characters of this hash.
        """
        working_dir_conda = working_dir / ".snakemake/conda"

        md5 = hashlib.md5()
        md5.update(working_dir_conda.absolute().as_posix().encode())
        md5.update(env.read_bytes())
        updated_hash = md5.hexdigest()[:8]
        return working_dir_conda / updated_hash

    def copy_env(self, env_name: str, working_dir: Union[str, Path]) -> None:
        """Copy a conda environment into a new working directory.

        Snakemake tries to enforce reproducibility to encode not only the
        environment file content but also the full path into the environment.
        Here we are mocking this by copying the cached env to the expected
        location by snakemake.

        ``{working_dir}/.snakemake/conda/{hash}``
        ``{working_dir}/.snakemake/conda/{hash}.yaml``

        Where ``{hash}`` is the md5sum of the full path
        ``{working_dir}/.snakemake/conda`` and the contents of the
        environment YAML file.
        """
        env_file_name = self.conda_env_path / f"{env_name}.yml"
        cache_path = self._get_env_cache_path(env_file_name)
        new_path = self._get_working_dir_env_path(env_file_name, Path(working_dir))

        shutil.copytree(cache_path, new_path)
        shutil.copyfile(env_file_name, new_path.as_posix() + ".yaml")

    def copy_all_envs(self, working_dir: Union[str, Path]) -> None:
        """Copy all conda environments into a new working directory.

        Snakemake tries to enforce reproducibility to encode not only the
        environment file content but also the full path into the environment.
        Here we are mocking this by copying the cached env to the expected
        location by snakemake.

        ``{working_dir}/.snakemake/conda/{hash}``
        ``{working_dir}/.snakemake/conda/{hash}.yaml``

        Where ``{hash}`` is the md5sum of the full path
        ``{working_dir}/.snakemake/conda`` and the contents of the
        environment YAML file.
        """
        for env_config in self.conda_env_path.glob("*.yml"):
            self.copy_env(env_config.stem, working_dir)