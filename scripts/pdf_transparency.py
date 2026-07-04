"""Shared transparency detection used by lulu_lint.py (to report it) and
flatten_transparency.py (to fix it). Kept in one place so the two scripts
can't drift out of sync on what counts as "transparent".

Detects PDF soft masks (/SMask, e.g. TikZ `path fading`) and transparency
groups (/Group << /S /Transparency >>) actually painted on each page.

This has to work from each page's own content stream rather than just
walking its /Resources dictionary: pgf/TikZ writes its named soft-mask
ExtGStates (e.g. `pgfsmask20`) into the resources of every page that loads
the pgf preamble, even pages that never paint with them — LaTeX/xelatex
reuses that same resource object verbatim across the whole document. A
resource-reachability scan would therefore flag nearly every page. Instead
this parses each page's content stream for the operators that actually
invoke a resource (`/Name gs` for an ExtGState, `/Name Do` for an
XObject), and only follows those specific names.
"""

import re

_GS_OP_RE = re.compile(rb"/([A-Za-z0-9+_.\-]+)\s+gs\b")
_DO_OP_RE = re.compile(rb"/([A-Za-z0-9+_.\-]+)\s+Do\b")
_SMASK_RE = re.compile(r"/SMask\s*(<<|\d+\s+0\s+R)")
_GROUP_RE = re.compile(r"/Group\s*<<[^>]*?/S\s*/Transparency", re.S)

_MAX_DEPTH = 6


def _lookup_key(doc, container_xref, key):
    try:
        return doc.xref_get_key(container_xref, key)
    except Exception:
        return None, None


def _resolve_dict_xref(doc, container_xref, key):
    """Resolve container_xref[key] to an xref number. Resources,
    resource-category dicts (ExtGState/XObject), and XObjects themselves
    are always indirect objects in xelatex's output, so this is all that's
    needed to walk from a page down to the resources it actually uses."""
    kind, value = _lookup_key(doc, container_xref, key)
    if kind == "xref":
        return int(value.split()[0])
    return None


def _entry_has_smask(doc, extgstate_cat_xref, name):
    kind, value = _lookup_key(doc, extgstate_cat_xref, name)
    if kind == "xref":
        raw = doc.xref_object(int(value.split()[0]), compressed=True)
    elif kind == "dict":
        raw = value
    else:
        return False
    return bool(_SMASK_RE.search(raw))


def _uses_transparency(doc, container_xref, content, seen_forms, depth=0):
    if depth > _MAX_DEPTH:
        return False
    res_xref = _resolve_dict_xref(doc, container_xref, "Resources")
    if res_xref is None:
        return False

    extgstate_xref = _resolve_dict_xref(doc, res_xref, "ExtGState")
    if extgstate_xref is not None:
        for name in {m.decode("latin1") for m in _GS_OP_RE.findall(content)}:
            if _entry_has_smask(doc, extgstate_xref, name):
                return True

    xobject_xref = _resolve_dict_xref(doc, res_xref, "XObject")
    if xobject_xref is not None:
        for name in {m.decode("latin1") for m in _DO_OP_RE.findall(content)}:
            form_xref = _resolve_dict_xref(doc, xobject_xref, name)
            if not form_xref or form_xref in seen_forms:
                continue
            seen_forms.add(form_xref)
            raw = doc.xref_object(form_xref, compressed=True)
            if "/Subtype/Form" not in raw.replace(" ", ""):
                continue  # images can't carry a nested group/resources
            if _GROUP_RE.search(raw):
                return True
            try:
                nested_content = doc.xref_stream(form_xref)
            except Exception:
                nested_content = b""
            if _uses_transparency(doc, form_xref, nested_content, seen_forms, depth + 1):
                return True
    return False


def find_transparent_pages(doc):
    """Return the 1-indexed page numbers whose own content actually paints
    with a soft mask or transparency group (not just pages that have one
    sitting unused in their resource dictionary)."""
    pages = []
    for pno in range(doc.page_count):
        page = doc[pno]
        content = b"".join(doc.xref_stream(x) for x in page.get_contents())
        if _uses_transparency(doc, page.xref, content, set()):
            pages.append(pno + 1)
    return pages
