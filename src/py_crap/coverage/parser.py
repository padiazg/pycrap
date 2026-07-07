import ast
import os
import xml.etree.ElementTree as ET
from typing import NamedTuple, Optional


class FunctionCoverage(NamedTuple):
    file: str
    package: str
    name: str
    line: int
    coverage: float


class ModuleCoverage(NamedTuple):
    dir: str
    module_path: str
    functions: list[FunctionCoverage]
    error: Optional[str] = None


def parse_coverage_xml(xml_path: str, mod_dir: str) -> ModuleCoverage:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    sources = root.findall(".//source")
    source_dir = ""
    for s in sources:
        if s.text:
            source_dir = s.text.strip()
            break

    package_elem = root.find(".//package")
    mod_path = package_elem.get("name", "") if package_elem is not None else ""

    functions: list[FunctionCoverage] = []

    for cls_elem in root.findall(".//class"):
        filename = cls_elem.get("filename", "")
        if not filename:
            continue

        pkg = mod_path
        if source_dir:
            abs_path = os.path.join(source_dir, filename) if not os.path.isabs(filename) else filename
        else:
            abs_path = os.path.join(mod_dir, filename) if not os.path.isabs(filename) else filename

        class_name = cls_elem.get("name", "")
        pkg = f"{pkg}.{class_name}" if pkg and class_name else pkg or class_name

        for line_elem in cls_elem.findall(".//line"):
            line_num = int(line_elem.get("number", 0))
            hits = int(line_elem.get("hits", 0))

            func_name = line_elem.get("name", "")
            if not func_name:
                func_name = _resolve_func_name(abs_path, line_num)

            coverage = 100.0 if hits > 0 else 0.0

            functions.append(
                FunctionCoverage(
                    file=abs_path,
                    package=pkg,
                    name=func_name,
                    line=line_num,
                    coverage=coverage,
                )
            )

    return ModuleCoverage(
        dir=mod_dir,
        module_path=mod_path,
        functions=functions,
    )


def _resolve_func_name(file_path: str, line_num: int) -> str:
    try:
        with open(file_path) as f:
            source = f.read()
    except OSError:
        return f"<unknown>@{line_num}"

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return f"<unknown>@{line_num}"

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = node.end_lineno or start
            if start <= line_num <= end:

                class_name = _enclosing_class(node)
                return f"{class_name}.{node.name}" if class_name else node.name

    return f"<unknown>@{line_num}"


def _enclosing_class(node: ast.FunctionDef) -> str:
    for parent in ast.walk(node):
        if isinstance(parent, ast.ClassDef):
            for child in parent.body:
                if child is node:
                    return parent.name
    return ""
