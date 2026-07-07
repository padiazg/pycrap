import ast

IGNORE_DIRECTIVES = {"# crap: ignore", "# gocyclo: ignore"}


def check_doc_ignore(node: ast.FunctionDef) -> bool:
    comment = node.body[0] if node.body else None
    if comment is None:
        return False

    if isinstance(comment, ast.Expr) and isinstance(comment.value, ast.Constant):
        docstr = comment.value.value
        if isinstance(docstr, str):
            for line in docstr.splitlines():
                stripped = line.strip().lower()
                if stripped in IGNORE_DIRECTIVES:
                    return True

    return False
