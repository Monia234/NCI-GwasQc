from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
from snakemake.rules import expand

import cgr_gwas_qc.yaml as yaml
from cgr_gwas_qc.models.config import Config
from cgr_gwas_qc.parsers.sample_sheet import SampleSheet


class CgrGwasQcConfigError(Exception):
    pass


class ConfigMgr:
    """Manage all things config.

    There should only be a single instance of this running at a time.

    Attributes:
        SRC_DIR (Path): The absolute path to ``cgr_gwas_qc`` source code.
        WORKFLOW_DIR (Path): The absolute path to the ``workflow`` source code.
        CONFIG_DIR (Path): The absolute path to the ``workflow/config``.
        RULE_DIR (Path): The absolute path to the ``workflow/rules``.
        SCRIPTS_DIR (Path): The absolute path to the ``workflow/scripts``.
        SNAKEFILE (Path): The absolute path to the ``workflow/Snakefile``.

        root (Path): The current working directory.
        user_config (Optional[Path]): The config.yml in the current working directory.
        user_patterns (Optional[Path]): The patterns.yml in the current working directory.

        config : Workflow configuration settings.
        ss: User's sample sheet data.

    Methods:
        expand: Uses columns from the user's sample sheet to expand a file pattern.
        conda: Creates the full path to conda environment.
        rules: Creates the full path to snakemake rule.
        scripts: Screates the full path to an internal script.
    """

    SRC_DIR = Path(__file__).parent.absolute()
    WORKFLOW_DIR = SRC_DIR / "workflow"

    CONDA_DIR = WORKFLOW_DIR / "conda"
    RULE_DIR = WORKFLOW_DIR / "rules"
    SCRIPTS_DIR = WORKFLOW_DIR / "scripts"
    SNAKEFILE = WORKFLOW_DIR / "Snakefile"

    __instance = None

    ################################################################################
    # Set-up
    ################################################################################
    def __init__(self, root: Path, user_config: Path, validate=True):
        self.root = root
        self.user_config = user_config

        if validate:
            self._config = Config(**yaml.load(self.user_config))
            self.sample_sheet_file = self.config.sample_sheet
            self._sample_sheet = SampleSheet(self.sample_sheet_file)
        else:
            # Force loading without validation. Use this only for debugging
            self._config = Config.construct(**yaml.load(self.user_config))
            try:
                self.sample_sheet_file = self.config.sample_sheet
                self._sample_sheet = SampleSheet(self.sample_sheet_file)
            except (AttributeError, FileNotFoundError):
                pass

    @classmethod
    def instance(cls, validate=True):
        """Returns the active ConfigMgr instance.

        This ensures that only 1 ConfigMgr is created per python session.
        """
        if cls.__instance is None:
            cls.__instance = cls(*find_configs(), validate)
        return cls.__instance

    ################################################################################
    # Access to the user's config and Sample Sheet
    ################################################################################
    @property
    def config(self) -> Config:
        return self._config

    @property
    def ss(self) -> pd.DataFrame:
        """Access the sample sheet DataFrame."""
        return self._sample_sheet.data

    ################################################################################
    # Helper functions for snakemake
    ################################################################################
    def expand(self, file_pattern, combination=zip) -> List[str]:
        """Use sample sheet columns to fill in file pattern"""
        return expand(file_pattern, combination, **self.ss.to_dict("list"))

    def conda(self, file_name: str) -> str:
        """Return path to a conda env file.

        Given a conda env file_name, prepends the full path to that file.
        """
        return (self.CONDA_DIR / file_name).as_posix()

    def rules(self, file_name: str) -> str:
        """Return the path to a rule file.

        Given a rule file_name, prepends the full path to that rule.
        """
        return (self.RULE_DIR / file_name).as_posix()

    def scripts(self, file_name: str) -> str:
        """Return the path to an interal script.

        Given a script file_name, prepends the full path to that script.
        """
        return (self.SCRIPTS_DIR / file_name).as_posix() + " "


################################################################################
# Helper functions for Set-up
################################################################################
def scan_for_yaml(base_dir: Path, name: str) -> Optional[Path]:
    """Scans a directory for Yaml configs.

    The Yaml format commonly has ``*.yml`` or ``*.yaml`` file extensions.
    This will search for ``{base_dir}/{name}.{yml,yaml}`` and returns
    the path if present.

    Returns:
        Optiona[Path]: Path to the config file
    """
    if (base_dir / f"{name}.yml").exists():
        return base_dir / f"{name}.yml"

    if (base_dir / f"{name}.yaml").exists():
        return base_dir / f"{name}.yaml"

    return None


def find_configs() -> Tuple[Path, Path]:
    root = Path.cwd().absolute()
    user_config = scan_for_yaml(root, "config")

    if user_config is None:
        raise FileNotFoundError("Please run with a `config.yml` in your working directory.")

    return root, user_config
