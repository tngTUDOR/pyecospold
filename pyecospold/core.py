"""Core Ecospold module containing parsing and saving functionalities."""
from io import StringIO
from pathlib import Path
from typing import List, Tuple, Union

from lxml import etree, objectify

from .config import Defaults
from .model_v1 import AdministrativeInformation as AdministrativeInformationV1
from .model_v1 import Allocation
from .model_v1 import DataEntryBy as DataEntryByV1
from .model_v1 import DataGeneratorAndPublication as DataGeneratorAndPublicationV1
from .model_v1 import Dataset, DataSetInformation
from .model_v1 import EcoSpold as EcoSpoldV1
from .model_v1 import Exchange
from .model_v1 import FlowData as FlowDataV1
from .model_v1 import Geography as GeographyV1
from .model_v1 import MetaInformation
from .model_v1 import ModellingAndValidation as ModellingAndValidationV1
from .model_v1 import Person, ProcessInformation, ReferenceFunction
from .model_v1 import Representativeness as RepresentativenessV1
from .model_v1 import Source
from .model_v1 import Technology as TechnologyV1
from .model_v1 import TimePeriod as TimePeriodV1
from .model_v1 import Validation
from .model_v2 import Activity, ActivityDataset, ActivityDescription
from .model_v2 import AdministrativeInformation as AdministrativeInformationV2
from .model_v2 import Classification, Comment
from .model_v2 import DataEntryBy as DataEntryByV2
from .model_v2 import DataGeneratorAndPublication as DataGeneratorAndPublicationV2
from .model_v2 import EcoSpold as EcoSpoldV2
from .model_v2 import ElementaryExchange, FileAttributes
from .model_v2 import FlowData as FlowDataV2
from .model_v2 import Geography as GeographyV2
from .model_v2 import ImpactIndicator, IntermediateExchange, MacroEconomicScenario
from .model_v2 import ModellingAndValidation as ModellingAndValidationV2
from .model_v2 import Parameter, Property
from .model_v2 import Representativeness as RepresentativenessV2
from .model_v2 import Review
from .model_v2 import Technology as TechnologyV2
from .model_v2 import TimePeriod as TimePeriodV2
from .model_v2 import TransferCoefficient, Uncertainty


class EcospoldLookupV1(etree.CustomElementClassLookup):
    """Custom XML lookup class for Ecospold V1 files."""

    def lookup(self, unused_node_type, unused_document, unused_namespace, name):
        """Maps Ecospold XML elements to custom Ecospold classes."""
        lookupmap = {
            "administrativeInformation": AdministrativeInformationV1,
            "allocation": Allocation,
            "dataEntryBy": DataEntryByV1,
            "dataGeneratorAndPublication": DataGeneratorAndPublicationV1,
            "dataset": Dataset,
            "dataSetInformation": DataSetInformation,
            "ecoSpold": EcoSpoldV1,
            "exchange": Exchange,
            "flowData": FlowDataV1,
            "geography": GeographyV1,
            "metaInformation": MetaInformation,
            "modellingAndValidation": ModellingAndValidationV1,
            "person": Person,
            "processInformation": ProcessInformation,
            "referenceFunction": ReferenceFunction,
            "representativeness": RepresentativenessV1,
            "source": Source,
            "technology": TechnologyV1,
            "timePeriod": TimePeriodV1,
            "validation": Validation,
        }
        try:
            return lookupmap[name]
        except KeyError:
            return None


class EcospoldLookupV2(etree.CustomElementClassLookup):
    """Custom XML lookup class for Ecospold V2 files."""

    def lookup(self, unused_node_type, unused_document, unused_namespace, name):
        """Maps Ecospold XML elements to custom Ecospold classes."""
        lookupmap = {
            "activity": Activity,
            "activityDataset": ActivityDataset,
            "activityDescription": ActivityDescription,
            "administrativeInformation": AdministrativeInformationV2,
            "allocationComment": Comment,
            "childActivityDataset": ActivityDataset,
            "classification": Classification,
            "comment": Comment,
            "dataEntryBy": DataEntryByV2,
            "dataGeneratorAndPublication": DataGeneratorAndPublicationV2,
            "ecoSpold": EcoSpoldV2,
            "elementaryExchange": ElementaryExchange,
            "fileAttributes": FileAttributes,
            "flowData": FlowDataV2,
            "generalComment": Comment,
            "geography": GeographyV2,
            "impactIndicator": ImpactIndicator,
            "intermediateExchange": IntermediateExchange,
            "macroEconomicScenario": MacroEconomicScenario,
            "modellingAndValidation": ModellingAndValidationV2,
            "parameter": Parameter,
            "property": Property,
            "representativeness": RepresentativenessV2,
            "review": Review,
            "technology": TechnologyV2,
            "timePeriod": TimePeriodV2,
            "transferCoefficient": TransferCoefficient,
            "uncertainty": Uncertainty,
        }
        try:
            return lookupmap[name]
        except KeyError:
            return None


def parse_file_v1(file: Union[str, Path, StringIO]) -> EcoSpoldV1:
    """Parses an Ecospold V1 XML file to custom Ecospold classes.

    Parameters:
    file: the str|Path path to the Ecospold XML file or its StringIO representation.

    Returns an EcoSpold class representing the root of the XML file.
    """
    return parse_file(file, Defaults.SCHEMA_V1_FILE, EcospoldLookupV1())


def parse_file_v2(file: Union[str, Path, StringIO]) -> EcoSpoldV2:
    """Parses an Ecospold V2 XML file to custom Ecospold classes.

    Parameters:
    file: the str|Path path to the Ecospold XML file or its StringIO representation.

    Returns an EcoSpold class representing the root of the XML file.
    """
    return parse_file(file, Defaults.SCHEMA_V2_FILE, EcospoldLookupV2())


def parse_file(
    file: Union[str, Path, StringIO],
    schema_path: str,
    ecospold_lookup: etree.CustomElementClassLookup,
) -> etree.ElementBase:
    """Parses an Ecospold XML file to custom Ecospold classes.

    Parameters:
    file: the str|Path path to the Ecospold XML file or its StringIO representation.
    schema_path: the path to the Ecospold XSD schema file.
    ecospold_lookup: the lookup class for mapping XML elements to EcoSpold classes.

    Returns an EcoSpold class representing the root of the XML file.
    """
    schema = etree.XMLSchema(file=schema_path)
    parser = objectify.makeparser(schema=schema)
    parser.set_element_class_lookup(ecospold_lookup)
    return objectify.parse(file, parser).getroot()


def validate_file(
    file: Union[str, Path, StringIO],
    schema_path: str,
) -> Union[None, List[str]]:
    """Validate a file against a given schema.

    Needed because the default parser doesn't provide any usable error context.

    Parameters:
    file: the str|Path path to the Ecospold XML file or its StringIO representation.
    schema_path: the path to the Ecospold XSD schema file.

    Returns ``None`` if the file validates, or a list of errors as strings.
    """
    schema = etree.XMLSchema(file=schema_path)
    doc = etree.parse(file)
    if not schema.validate(doc):
        return schema.error_log
    return None


def validate_file_v1(file: Union[str, Path, StringIO]) -> Union[None, List[str]]:
    """Validates an Ecospold V1 XML file to custom Ecospold classes.

    Parameters:
    file: the str|Path path to the Ecospold XML file or its StringIO representation.

    Returns ``None`` if valid or a list of error strings.
    """
    return validate_file(file, Defaults.SCHEMA_V1_FILE)


def validate_file_v2(file: Union[str, Path, StringIO]) -> Union[None, List[str]]:
    """Parses an Ecospold V2 XML file to custom Ecospold classes.

    Parameters:
    file: the str|Path path to the Ecospold XML file or its StringIO representation.

    Returns ``None`` if valid or a list of error strings.
    """
    return validate_file(file, Defaults.SCHEMA_V2_FILE)


def parse_directory_v1(
    dir_path: Union[str, Path], valid_suffixes: Union[List[str], None] = None
) -> List[Tuple[Path, EcoSpoldV1]]:
    """Parses a directory of Ecospold XML files to a list of custom Ecospold classes.

    Parameters:
    dir_path: the directory path, should contain files of version 1 of EcoSpold.
    valid_suffixes: a list of valid file suffixes which will only be considered for
    parsing. If None, defaults to [".xml", ".spold"].

    Returns a list of tuples of file paths and corresponding EcoSpold classes
    representing the root of the XML file.
    """
    return parse_directory(
        dir_path=dir_path,
        schema_path=Defaults.SCHEMA_V1_FILE,
        ecospold_lookup=EcospoldLookupV1(),
        valid_suffixes=valid_suffixes,
    )


def parse_directory_v2(
    dir_path: Union[str, Path], valid_suffixes: Union[List[str], None] = None
) -> List[Tuple[Path, EcoSpoldV2]]:
    """Parses a directory of Ecospold XML files to a list of custom Ecospold classes.

    Parameters:
    dir_path: the directory path, should contain files of version 2 of EcoSpold.
    valid_suffixes: a list of valid file suffixes which will only be considered for
    parsing. If None, defaults to [".xml", ".spold"].

    Returns a list of tuples of file paths and corresponding EcoSpold classes
    representing the root of the XML file.
    """
    return parse_directory(
        dir_path=dir_path,
        schema_path=Defaults.SCHEMA_V2_FILE,
        ecospold_lookup=EcospoldLookupV2(),
        valid_suffixes=valid_suffixes,
    )


def parse_directory(
    dir_path: Union[str, Path],
    schema_path: str,
    ecospold_lookup: etree.CustomElementClassLookup,
    valid_suffixes: Union[List[str], None] = None,
) -> List[Tuple[Path, etree.ElementBase]]:
    """Parses a directory of Ecospold XML files to a list of custom Ecospold classes.

    Parameters:
    dir_path: the directory path, should contain files of only the schema_path version.
    schema_path: the path to the Ecospold XSD schema file.
    ecospold_lookup: the lookup class for mapping XML elements to EcoSpold classes.
    valid_suffixes: a list of valid file suffixes which will only be considered for
    parsing. If None, defaults to [".xml", ".spold"].

    Returns a list of tuples of file paths and corresponding EcoSpold classes
    representing the root of the XML file.
    """
    if valid_suffixes is None:
        valid_suffixes = [".xml", ".spold"]

    dir_path = Path(dir_path).resolve()
    return [
        (
            file_path,
            parse_file(
                file=file_path, schema_path=schema_path, ecospold_lookup=ecospold_lookup
            ),
        )
        for file_path in dir_path.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in valid_suffixes
    ]


def save_file(root: etree.ElementBase, path: str) -> None:
    """Saves an Ecospold class to an XML file.

    Parameters:
    root: the EcoSpold class representing the root of the XML file.
    path: the path to save the Ecospold XML file.
    """
    root = etree.ElementTree(root)
    root.write(path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
