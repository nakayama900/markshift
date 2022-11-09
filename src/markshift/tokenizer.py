# -*- coding: utf-8 -*-
from lark import Lark, Transformer, v_args
from lark import logger
import lark
import uuid
import logging
logger.setLevel(logging.DEBUG)

grammar = """
    ?start: expr_command
          | statement

    ?expr_command: "[@" command_name (space_sep parameter)* "]" -> expr_command
    ?space_sep: WS_INLINE+ -> space_sep
    ?command_name: COMMAND
    ?parameter: WWORD -> parameter

    ?statement: [expr|raw_sentence]*

    ?expr: expr_url_only
         | expr_url_title
         | expr_title_url
         | expr_builtin_symbols
         | expr_math
         | expr_img

    ?expr_url_only: "[" url "]"
    ?expr_url_title: "[" url space_sep url_title "]"
    ?expr_title_url: "[" url_title space_sep url "]"
    ?url: URL
    ?url_title: WWORD -> url_title

    ?expr_builtin_symbols: "[" symbols_applied space_sep statement "]"
    ?symbols_applied: BUILTIN_NESTABLE_SYMBOLS+ -> symbols
    ?expr_math: "[$" space_sep latex_math_expr "$]"
    ?expr_img: "[@img" space_sep img_path "]" -> expr_img_path_only
             | "[@img" space_sep img_path space_sep alt_img "]" -> expr_img_path_alt
             | "[@img" space_sep alt_img space_sep img_path "]" -> expr_alt_img_path
    ?img_path: URL | FILE_PATH
    ?alt_img: ESCAPED_STRING

    ?raw_sentence: (NON_SQB_WORD|WS_INLINE)+ -> raw_sentence
    ?latex_math_expr: /.+?(?=\$\])/ -> latex_math_expr
    // match other than "$]"

    COMMAND: "math" | "quote" | "code"
    BUILTIN_NESTABLE_SYMBOLS: "*" | "/"
    LCASE_LETTER: "a".."z"
    UCASE_LETTER: "A".."Z"
    HIRAGANA_LETTER: /\p{Hiragana}/
    KATAKANA_LETTER: /\p{Katakana}/
    KANJI_LETTER: /\p{Han}/
    LETTER: UCASE_LETTER | LCASE_LETTER
    WORD: LETTER+
    WLETTER: UCASE_LETTER | LCASE_LETTER | HIRAGANA_LETTER | KATAKANA_LETTER | KANJI_LETTER
    WWORD: WLETTER+

    MATH_SYMBOL: /[^\p{L}\d\s]/u

    FILE_PATH: /([\/]?[\w_\-\s0-9\.]+)+\.([^\s\]]*)/u


    NONSQB: /[^\[\]]/
    NON_SQB_WORD: NONSQB+
    URL: /\w+:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+/
    %import common.WS_INLINE
    %import common.ESCAPED_STRING
    %import common.NUMBER
"""

tokenizer = Lark(grammar, parser='earley', keep_all_tokens=False, regex=True, g_regex_flags=1, debug=False) #, transformer=CalculateTree())

from .element import *
@v_args(inline=True)    # Affects the signatures of the methods
class ElementTransformer(Transformer):
    def __init__(self, renderer):
        self.renderer = renderer

    def parameter(self, param):
        return param.value

    def space_sep(self, *args):
        return lark.visitors.Discard

    def expr_command(self, command, *params):
        command_name = command.value
        if command_name == 'quote':
            return QuoteElement(parent=None, renderer=self.renderer)
        elif command_name == 'code':
            if len(params) > 1:
                raise ValueError('too many parameters for code')
            return CodeElement(parent=None, lang=params[0], renderer=self.renderer)
        elif command_name == 'math':
            return MathElement(parent=None, content=params[0], renderer=self.renderer, inline=False)
        return 

    def symbols(self, *tokens):
        return [t.value for t in tokens]

    def expr_builtin_symbols(self, symbols, *elements):
        def _strong(child_elems):
            elem = StrongElement(parent=None, renderer=self.renderer)
            elem.child_elements.extend(child_elems)
            return elem
        def _italic(child_elems):
            elem = ItalicElement(parent=None, renderer=self.renderer)
            elem.child_elements.extend(child_elems)
            return elem
        assert(len(symbols) > 0)
        child = list(elements)
        for s in symbols:
            if s == '*':
                child = [_strong(child)]
            elif s == '/':
                child = [_italic(child)]
        return child[0]

    def expr_math(self, latex_math):
        return MathElement(parent=None, content=latex_math, renderer=self.renderer, uid=uuid.uuid4(), inline=True)

    def latex_math_expr(self, *tokens):
        mathexpr = ''.join([t.value for t in tokens])
        return mathexpr
        # return TextElement(parent=None, content=mathexpr, renderer=self.renderer)

    def raw_sentence(self, text):
        return TextElement(parent=None, content=text.value, renderer=self.renderer)

    def statement(self, *elements):
        compound = Element(parent=None, renderer=self.renderer)
        compound.child_elements.extend(elements)
        return compound

    def URL(self, url):
        return url.value

    def url_title(self, url_title):
        return url_title.value

    def expr_url_only(self, url):
        return LinkElement(parent=None, content='', link=url, renderer=self.renderer)

    def expr_url_title(self, url, title):
        return LinkElement(parent=None, content=title, link=url, renderer=self.renderer)

    def expr_title_url(self, title, url):
        return LinkElement(parent=None, content=title, link=url, renderer=self.renderer)

    def FILE_PATH(self, path):
        return path.value

    def ESCAPED_STRING(self, s):
        return s[1:-2]

    def expr_img_path_only(self, path):
        return ImageElement(parent=None, src=path, alt='', renderer=self.renderer)

    def expr_img_path_alt(self, path, alt):
        return ImageElement(parent=None, src=path, alt=alt, renderer=self.renderer)

    def expr_alt_img_path(self, alt, path):
        return ImageElement(parent=None, src=path, alt=alt, renderer=self.renderer)