from typing import List


class GwasQcValidationError(Exception):
    pass


################################################################################
# BGZIP
################################################################################
class BgzipError(GwasQcValidationError):
    pass


class BgzipMagicNumberError(BgzipError):
    def __init__(self, name):
        message = f"{name} is missing the GZIP magic number."
        super().__init__(message)


class BgzipTruncatedFileError(BgzipError):
    def __init__(self, name):
        message = f"{name} is missing the EOF mark."
        super().__init__(message)


################################################################################
# BPM
################################################################################
class BpmError(GwasQcValidationError):
    pass


class BpmMagicNumberError(BpmError):
    def __init__(self, name):
        message = f"{name} has missing or wrong BPM magic number."
        super().__init__(message)


class BpmVersionError(BpmError):
    def __init__(self, name):
        message = f"{name} has unknown or unsupported BPM version."
        super().__init__(message)


class BpmNormalizationError(BpmError):
    def __init__(self, name):
        message = f"{name} has an invalid normalization ID."
        super().__init__(message)


class BpmEntryError(BpmError):
    def __init__(self, name):
        message = f"{name} has an invalid number of assay entries."
        super().__init__(message)


################################################################################
# GTC
################################################################################
class GtcError(GwasQcValidationError):
    pass


class GtcMagicNumberError(GtcError):
    def __init__(self):
        message = "Missing or wrong GTC magic number."
        super().__init__(message)


class GtcVersionError(GtcError):
    def __init__(self):
        message = "Unknown or unsupported GTC version."
        super().__init__(message)


class GtcTruncatedFileError(GtcError):
    def __init__(self):
        message = "Missing the EOF mark."
        super().__init__(message)


################################################################################
# IDAT
################################################################################
class IdatError(GwasQcValidationError):
    pass


class IdatMagicNumberError(IdatError):
    def __init__(self):
        message = "Missing or wrong IDAT magic number."
        super().__init__(message)


class IdatTruncatedFileError(IdatError):
    def __init__(self):
        message = "Missing the EOF metadata."
        super().__init__(message)


################################################################################
# Sample Sheet
################################################################################
class SampleSheetError(GwasQcValidationError):
    pass


class SampleSheetMissingSectionHeaderError(SampleSheetError):
    def __init__(self, name: str, missing_headers: List[str]):
        self.missing_headers = missing_headers
        header_str = ", ".join(missing_headers)
        message = f"{name} is missing sections: {header_str}"
        super().__init__(message)


class SampleSheetTruncatedFileError(SampleSheetError):
    def __init__(self, name: str):
        message = f"{name} is truncated."
        super().__init__(message)


class SampleSheetNullRowError(SampleSheetError):
    def __init__(self, name: str):
        message = f"{name} has completely empty rows."
        super().__init__(message)


class SampleSheetMissingRequiredColumnsError(SampleSheetError):
    def __init__(self, name: str, missing_required_columns: List[str]):
        col_str = ", ".join(missing_required_columns)
        message = f"{name} is missing the required columns: {col_str}"
        super().__init__(message)


class SampleSheetMissingValueRequiredColumnsError(SampleSheetError):
    def __init__(self, name: str, col_w_missing_values: List[str]):
        col_str = ", ".join(col_w_missing_values)
        message = f"{name} had missing values in required columns: {col_str}"
        super().__init__(message)
