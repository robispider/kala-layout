"""Wikitext → running prose (cleaning version ``bnwiki-prose-v1``).

Most pages of Kala's atomic Wikipedia dump are raw wikitext; a few carry a
``kalaCanonicalProse`` attribute and are already prose. Cleaning keeps only
paragraph text a person would type:

* removed with their content: comments, ``<ref>``, non-prose tags (math,
  gallery, timeline, code, …), templates ``{{…}}``, template parameters,
  tables ``{|…|}``, file/category/interlanguage links, bare URLs;
* replaced by their visible text: internal links (label or target),
  external links (label), bold/italic quotes, other HTML tags;
* paragraph filter: lines that are headings, list or table rows, or still
  contain markup are dropped; a paragraph needs at least ``MIN_TOKENS``
  tokens and a Bengali share of at least ``MIN_BENGALI_SHARE`` of its letters.

Template removal leaves gaps such as ``( ; অর্থাৎ``; empty brackets and
spaces before closing punctuation are tidied, since typed text has neither.
"""
from __future__ import annotations

import html
import re
import unicodedata

VERSION = "bnwiki-prose-v1"
MIN_TOKENS = 3
MIN_BENGALI_SHARE = 0.75

_COMMENT = re.compile(r"<!--.*?(?:-->|$)", re.S)
_REF_SELF = re.compile(r"<ref\b[^>]*/\s*>", re.I)
_REF = re.compile(r"<ref\b[^>]*>.*?(?:</ref\s*>|$)", re.I | re.S)
# Block tags whose content is never prose; inline formatting tags keep their content (handled by _TAG).
_BLOCK = re.compile(r"<(math|chem|ce|gallery|timeline|syntaxhighlight|source|pre|code|score|graph|mapframe|"
                    r"maplink|imagemap|templatedata|templatestyles|references|hiero|inputbox|categorytree|"
                    r"charinsert|indicator|table)\b[^>]*?(?:/>|>.*?(?:</\1\s*>|$))", re.I | re.S)
_PARAM = re.compile(r"\{\{\{[^{}]*\}\}\}")
_TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
_TABLE = re.compile(r"\{\|(?:(?!\{\|)[^\0])*?\|\}")
_LINK = re.compile(r"\[\[([^\[\]|]*)(?:\|([^\[\]]*))?\]\]")
_EXT_LINK = re.compile(r"\[(?:(?:https?|ftp):)?//[^\s\]]*\s*([^\]]*)\]")
_URL = re.compile(r"(?:https?|ftp)://\S+")
_TAG = re.compile(r"</?[a-zA-Z][^<>]*>")
_QUOTES = re.compile(r"'{2,}")
_MAGIC = re.compile(r"__[A-Z]+__")
_EMPTY_BRACKETS = re.compile(r"\(\s*[,;:।]?\s*\)")
_OPEN_GAP = re.compile(r"\(\s*[,;]\s*")
_SPACE_BEFORE = re.compile(r"\s+([,;:।?!)])")
_SPACE_AFTER_OPEN = re.compile(r"\(\s+")
_SPACES = re.compile(r"[ \t]{2,}")

_DROPPED_NAMES = {"file", "image", "media", "category", "চিত্র", "ফাইল", "মিডিয়া", "বিষয়শ্রেণী",
                      "উইকিপিডিয়া", "wikipedia", "wp", "টেমপ্লেট", "template", "special", "বিশেষ",
                      "ব্যবহারকারী", "user", "পোর্টাল", "portal", "সাহায্য", "help", "মডিউল", "module"}
# The dump stores ড় ঢ় য় precomposed; compare namespace names in NFC.
DROPPED_NAMESPACES = {unicodedata.normalize("NFC", name) for name in _DROPPED_NAMES}
_INTERWIKI = re.compile(r"^:?[a-z]{2,3}(?:-[a-z]+)*:")
LINE_SKIP_PREFIXES = ("=", "*", "#", ":", ";", "|", "!", "{", "}", "----", "<")
MARKUP_RESIDUE = ("{{", "}}", "[[", "]]", "{|", "|}", "|", "<", ">", "{", "}", "&lt;", "&gt;")


def _replace_link(match: re.Match) -> str:
    target, label = match.group(1).strip(), match.group(2)
    lowered = unicodedata.normalize("NFC", target.lstrip(":").lower())
    prefix = lowered.split(":", 1)[0].strip() if ":" in lowered else None
    if prefix is not None and (prefix in DROPPED_NAMESPACES or _INTERWIKI.match(lowered)):
        return "" if not target.startswith(":") or label is None else label
    if label is None or not label.strip():
        return target.split("#", 1)[0]
    return label


def _repeat(pattern: re.Pattern, text: str, replacement="", limit: int = 20) -> str:
    for _ in range(limit):
        text, n = pattern.subn(replacement, text)
        if not n:
            break
    return text


def strip_markup(text: str) -> str:
    text = _COMMENT.sub("", text)
    text = _REF_SELF.sub("", text)
    text = _REF.sub("", text)
    text = _BLOCK.sub("", text)
    text = _repeat(_PARAM, text)
    text = _repeat(_TEMPLATE, text)
    text = _repeat(_TABLE, text)
    text = _repeat(_LINK, text, _replace_link)
    text = _EXT_LINK.sub(lambda m: m.group(1), text)
    text = _URL.sub("", text)
    text = _TAG.sub("", text)
    text = _QUOTES.sub("", text)
    text = _MAGIC.sub("", text)
    return text


def _bengali_share(line: str) -> tuple[int, float]:
    letters = bengali = 0
    for ch in line:
        if ch.isalpha():
            letters += 1
            if "ঀ" <= ch <= "৿":
                bengali += 1
    return bengali, (bengali / letters if letters else 0.0)


def tidy(line: str) -> str:
    line = _EMPTY_BRACKETS.sub("", line)
    line = _OPEN_GAP.sub("(", line)
    line = _SPACE_AFTER_OPEN.sub("(", line)
    line = _SPACE_BEFORE.sub(r"\1", line)
    return _SPACES.sub(" ", line).strip()


def paragraphs(text: str, prose: bool, stats: dict | None = None) -> list[str]:
    """Candidate prose paragraphs of a page (not yet Unicode-normalized)."""
    if not prose:
        text = strip_markup(text)
    text = html.unescape(text)
    out = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        reason = None
        if line.startswith(LINE_SKIP_PREFIXES):
            reason = "structure"
        elif any(mark in line for mark in MARKUP_RESIDUE):
            reason = "markup"
        else:
            line = tidy(line)
            bengali, share = _bengali_share(line)
            if len(line.split()) < MIN_TOKENS:
                reason = "short"
            elif share < MIN_BENGALI_SHARE:
                reason = "not_bangla"
        if reason is None:
            out.append(line)
        if stats is not None:
            stats[reason or "kept"] = stats.get(reason or "kept", 0) + 1
    return out


def describe() -> dict:
    return {"version": VERSION, "min_tokens": MIN_TOKENS, "min_bengali_letter_share": MIN_BENGALI_SHARE,
            "dropped_link_namespaces": sorted(DROPPED_NAMESPACES),
            "line_skip_prefixes": list(LINE_SKIP_PREFIXES), "markup_residue": list(MARKUP_RESIDUE)}
