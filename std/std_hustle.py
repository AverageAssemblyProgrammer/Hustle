from functools import cached_property
from arrow_strings.strings_with_arrows import *
from keywords.keywords import *
from ops.ops import *
import string
import os
import math
from sys import *
import sys
import time 
import random
import subprocess
import shlex
from os import path

# TODO: implement game of life in hustle

sys.setrecursionlimit(10000000)

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

class Error:
  def __init__(self, pos_start, pos_end, error_name, details):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details
  
  def as_string(self):
    result  = f'{self.error_name}: {self.details}\n'
    result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

class IllegalCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, pos_start, pos_end, details=''):
    super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
  def __init__(self, pos_start, pos_end, details, context):
    super().__init__(pos_start, pos_end, 'Runtime Error', details)
    self.context = context

  def as_string(self):
    result  = self.generate_traceback()
    result += f'{self.error_name}: {self.details}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

  def generate_traceback(self):
    result = ''
    pos = self.pos_start
    ctx = self.context

    while ctx:
      result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
      pos = ctx.parent_entry_pos
      ctx = ctx.parent

    return 'Traceback (most recent call last):\n' + result

class Position:
  def __init__(self, idx, ln, col, fn, ftxt):
    self.idx = idx
    self.ln = ln
    self.col = col
    self.fn = fn
    self.ftxt = ftxt

  def advance(self, current_char=None):
    self.idx += 1
    self.col += 1

    if current_char == '\n':
      self.ln += 1
      self.col = 0

    return self

  def copy(self):
    return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value

    if pos_start:
      self.pos_start = pos_start.copy()
      self.pos_end = pos_start.copy()
      self.pos_end.advance()

    if pos_end:
      self.pos_end = pos_end.copy()

  def matches(self, type_, value):
    return self.type == type_ and self.value == value
  
  def __repr__(self):
    if self.value: return f'{self.type}:{self.value}'
    return f'{self.type}'


class Lexer:
  def __init__(self, fn, text):
    self.fn = fn
    self.text = text
    self.pos = Position(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()
  
  def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

  def make_tokens(self):
    tokens = []

    while self.current_char != None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char == '#':
        self.skip_comment()
      elif self.current_char in ';\n':
        tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
        self.advance()
      elif self.current_char in DIGITS:
        tokens.append(self.make_number())
      elif self.current_char in LETTERS:
        tokens.append(self.make_identifier())
      elif self.current_char == '"':
        tokens.append(self.make_string())
      elif self.current_char == '+':
        tokens.append(Token(TT_PLUS, pos_start=self.pos))
        self.advance()
      elif self.current_char == '-':
        tokens.append(self.make_minus_or_arrow())
      elif self.current_char == '*':
        tokens.append(Token(TT_MUL, pos_start=self.pos))
        self.advance()
      elif self.current_char == '%':
        tokens.append(Token(TT_MOD, pos_start=self.pos))
        self.advance()
      elif self.current_char == '/':
        tokens.append(Token(TT_DIV, pos_start=self.pos))
        self.advance()
      elif self.current_char == '^':
        tokens.append(Token(TT_POW, pos_start=self.pos))
        self.advance()
      elif self.current_char == '(':
        tokens.append(Token(TT_LPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == ')':
        tokens.append(Token(TT_RPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '[':
        tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == ']':
        tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '!':
        token, error = self.make_not_equals()
        if error: return [], error
        tokens.append(token)
      elif self.current_char == '=':
        tokens.append(self.make_equals())
      elif self.current_char == '<':
        tokens.append(self.make_less_than())
      elif self.current_char == '>':
        tokens.append(self.make_greater_than())
      elif self.current_char == ',':
        tokens.append(Token(TT_COMMA, pos_start=self.pos))
        self.advance()
      else:
        pos_start = self.pos.copy()
        char = self.current_char
        self.advance()
        return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    tokens.append(Token(TT_EOF, pos_start=self.pos))
    return tokens, None

  def make_number(self):
    num_str = ''
    dot_count = 0
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in DIGITS + '.':
      if self.current_char == '.':
        if dot_count == 1: break
        dot_count += 1
      num_str += self.current_char
      self.advance()

    if dot_count == 0:
      return Token(TT_INT, int(num_str), pos_start, self.pos)
    else:
      return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

  def make_string(self):
    string = ''
    pos_start = self.pos.copy()
    escape_character = False
    self.advance()

    escape_characters = {
      'n': '\n',
      't': '\t'
    }
    while self.current_char != None and (self.current_char != '"' or escape_character):
      if escape_character:
        string += escape_characters.get(self.current_char, self.current_char)
      else:
        if self.current_char == '\\':
          escape_character = True
        else:
          string += self.current_char
      self.advance()
      escape_character = False
    
    self.advance()
    return Token(TT_STRING, string, pos_start, self.pos)


  def make_identifier(self):
    id_str = ''
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
      id_str += self.current_char
      self.advance()

    tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
    return Token(tok_type, id_str, pos_start, self.pos)

  def make_minus_or_arrow(self):
    tok_type = TT_MINUS
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '>':
      self.advance()
      tok_type = TT_ARROW

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_not_equals(self):
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

    self.advance()
    return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")
  
  def make_equals(self):
    tok_type = TT_EQ
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_EE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_less_than(self):
    tok_type = TT_LT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=':
      self.advance()
      tok_type = TT_LTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def make_greater_than(self):
    tok_type = TT_GT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == '=': 
      self.advance()
      tok_type = TT_GTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  def skip_comment(self):
    self.advance()
    while self.current_char != '\n':
      self.advance()

class NumberNode:
  def __init__(self, tok):
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class StringNode:
  def __init__(self, tok):
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

class ListNode:
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes

    self.pos_start = pos_start
    self.pos_end = pos_end

class VarAccessNode:
  def __init__(self, var_name_tok):
    self.var_name_tok = var_name_tok

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end

class VarAssignNode:
  def __init__(self, var_name_tok, value_node):
    self.var_name_tok = var_name_tok
    self.value_node = value_node

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end

class BinOpNode:
  def __init__(self, left_node, op_tok, right_node):
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node

    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

  def __repr__(self):
    return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
  def __init__(self, op_tok, node):
    self.op_tok = op_tok
    self.node = node

    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end

  def __repr__(self):
    return f'({self.op_tok}, {self.node})'

class IfNode:
  def __init__(self, cases, else_case):
    self.cases = cases
    self.else_case = else_case

    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end  

class IncludeNode:
  def __init__(self, include_name, body_node, should_return_null):
    self.include_name = include_name
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.include_name.pos_start
    self.pos_end = self.include_name.pos_end

class MakeIntNode:
  def __init__(self, int_tok, body_node, should_return_null):
    self.int_tok = int_tok
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.int_tok.pos_start
    self.pos_end = self.int_tok.pos_end

class MakeFloatNode:
  def __init__(self, float_tok, body_node, should_return_null):
    self.float_tok = float_tok
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.float_tok.pos_start
    self.pos_end = self.float_tok.pos_end

class MakeStrNode:
  def __init__(self, string_tok, body_node, should_return_null):
    self.string_tok = string_tok
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.string_tok.pos_start
    self.pos_end = self.string_tok.pos_end

class ExitNode:
  def __init__(self, exit_code, body_node, should_return_null):
    self.exit_code = exit_code
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.exit_code.pos_start
    self.pos_end = self.exit_code.pos_end 

class ArgvNode:
  def __init__(self, argv_count, body_node, should_return_null):
    self.argv_count = argv_count
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.argv_count.pos_start
    self.pos_end = self.argv_count.pos_end 

class ShuffleNode:
  def __init__(self, list_name, body_node, should_return_null):
    self.list_name = list_name
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.list_name.pos_start
    self.pos_end = self.list_name.pos_end

class lenStrNode:
  def __init__(self, string_tok, body_node, should_return_null):
    self.string_tok = string_tok
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.string_tok.pos_start
    self.pos_end = self.string_tok.pos_end

class takeElementNode:
  def __init__(self, list_name, index_name, body_node, should_return_null):
    self.list_name = list_name
    self.index_name = index_name
    self.body_node = body_node
    self.should_return_null = should_return_null 

    self.pos_start = self.list_name.pos_start
    self.pos_end   = self.index_name.pos_end

class randIntNode:
  def __init__(self, first_rand_name, second_rand_name, body_node, should_return_null):
    self.first_rand_name = first_rand_name
    self.second_rand_name = second_rand_name
    self.body_node = body_node
    self.should_return_null = should_return_null 

    self.pos_start = self.first_rand_name.pos_start
    self.pos_end   = self.second_rand_name.pos_end

class SystemNode:
  def __init__(self, system_command_name, body_node, should_return_null):
    self.system_command_name = system_command_name
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.system_command_name.pos_start
    self.pos_end = self.system_command_name.pos_end

class SleepNode: 
  def __init__(self, time_name, body_node, should_return_null):
    self.time_name = time_name
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.time_name.pos_start
    self.pos_end = self.time_name.pos_end

class ForNode:
  def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
    self.var_name_tok = var_name_tok
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.step_value_node = step_value_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.body_node.pos_end


class WhileNode:
  def __init__(self, condition_node, body_node, should_return_null):
    self.condition_node = condition_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end

class FuncDefNode:
  def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
    self.var_name_tok = var_name_tok
    self.arg_name_toks = arg_name_toks
    self.body_node = body_node
    self.should_auto_return = should_auto_return

    if self.var_name_tok:
      self.pos_start = self.var_name_tok.pos_start
    elif len(self.arg_name_toks) > 0:
      self.pos_start = self.arg_name_toks[0].pos_start
    else:
      self.pos_start = self.body_node.pos_start

    self.pos_end = self.body_node.pos_end

class CallNode:
  def __init__(self, node_to_call, arg_nodes):
    self.node_to_call = node_to_call
    self.arg_nodes = arg_nodes

    self.pos_start = self.node_to_call.pos_start

    if len(self.arg_nodes) > 0:
      self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
    else:
      self.pos_end = self.node_to_call.pos_end

class ReturnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return

    self.pos_start = pos_start
    self.pos_end = pos_end


class ContinueNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end

class BreakNode:
  def __init__(self, pos_start, pos_end):
    self.pos_start = pos_start
    self.pos_end = pos_end

class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0

  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  def success(self, node):
    self.node = node
    return self

  def failure(self, error):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()

  def advance(self):
    self.tok_idx += 1
    self.update_current_tok()
    return self.current_tok

  def reverse(self, amount=1):
    self.tok_idx -= amount
    self.update_current_tok()
    return self.current_tok

  def update_current_tok(self):
    if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]

  def parse(self):
    res = self.statements()
    if not res.error and self.current_tok.type != TT_EOF:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Token cannot appear after previous tokens"
      ))
    return res

  def statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_tok.pos_start.copy()

    while self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    while True:
      newline_count = 0
      while self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()
        newline_count += 1
      if newline_count == 0:
        more_statements = False
      
      if not more_statements: break
      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue
      statements.append(statement)

    return res.success(ListNode(
      statements,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def statement(self):
    res = ParseResult()
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.matches(TT_KEYWORD, 'return'):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
    
    if self.current_tok.matches(TT_KEYWORD, 'continue'):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

    if self.current_tok.matches(TT_KEYWORD, 'break'):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'return', 'continue', 'break', 'var', 'if', 'for', 'while', 'fun', int, float, identifier, '+', '-', '(', '[' or 'not'"
      ))
    return res.success(expr)

  def expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'var'):
      res.register_advancement()
      self.advance()
    
      if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected identifier"
        ))

      var_name = self.current_tok
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_EQ:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected '='"
        ))

      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      return res.success(VarAssignNode(var_name, expr))

    node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'not'"
      ))

    return res.success(node)


  def comp_expr(self):
    res = ParseResult()

    if self.current_tok.matches(TT_KEYWORD, 'not'):
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error: return res
      return res.success(UnaryOpNode(op_tok, node))
    
    node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))
    
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while', 'func' or 'not'"
      ))

    return res.success(node)

  def arith_expr(self):
    return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

  def term(self):
    return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_MOD))

  def factor(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_PLUS, TT_MINUS):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  def power(self):
    return self.bin_op(self.call, (TT_POW, ), self.factor)

  def call(self):
    res = ParseResult()
    atom = res.register(self.atom())
    if res.error: return res

    if self.current_tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      arg_nodes = []

      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
      else:
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ')', 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'not'"
          ))

        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          arg_nodes.append(res.register(self.expr()))
          if res.error: return res

        if self.current_tok.type != TT_RPAREN:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ')'"
          ))

        res.register_advancement()
        self.advance()
      return res.success(CallNode(atom, arg_nodes))
    return res.success(atom)

  def atom(self):
    res = ParseResult()
    tok = self.current_tok

    if tok.type in (TT_INT, TT_FLOAT):
      res.register_advancement()
      self.advance()
      return res.success(NumberNode(tok))

    elif tok.type == TT_STRING:
      res.register_advancement()
      self.advance()
      return res.success(StringNode(tok))

    elif tok.type == TT_IDENTIFIER:
      res.register_advancement()
      self.advance()
      return res.success(VarAccessNode(tok))

    elif tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
        return res.success(expr)
      else:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ')'"
        ))

    elif tok.type == TT_LSQUARE:
      list_expr = res.register(self.list_expr())
      if res.error: return res
      return res.success(list_expr)
    
    elif tok.matches(TT_KEYWORD, 'if'):
      if_expr = res.register(self.if_expr())
      if res.error: return res
      return res.success(if_expr)

    elif tok.matches(TT_KEYWORD, 'for'):
      for_expr = res.register(self.for_expr())
      if res.error: return res
      return res.success(for_expr)

    elif tok.matches(TT_KEYWORD, 'include'):
      include_expr = res.register(self.include_expr())
      if res.error: return res
      return res.success(include_expr)

    elif tok.matches(TT_KEYWORD, 'Exit'):
      Exit_expr = res.register(self.Exit_expr())
      if res.error: return res
      return res.success(Exit_expr)
    
    elif tok.matches(TT_KEYWORD, 'make_str'):
      make_str_expr = res.register(self.make_str_expr())
      if res.error: return res
      return res.success(make_str_expr)    

    elif tok.matches(TT_KEYWORD, 'make_int'):
      make_int_expr = res.register(self.make_int_expr())
      if res.error: return res
      return res.success(make_int_expr)

    elif tok.matches(TT_KEYWORD, 'make_float'):
      make_float_expr = res.register(self.make_float_expr())
      if res.error: return res
      return res.success(make_float_expr)

    elif tok.matches(TT_KEYWORD, 'Argv'):
      argv_expr = res.register(self.argv_expr())
      if res.error: return res
      return res.success(argv_expr)

    elif tok.matches(TT_KEYWORD, 'randInt'):
      randInt_expr = res.register(self.randInt_expr())
      if res.error: return res
      return res.success(randInt_expr)

    elif tok.matches(TT_KEYWORD, 'takeElement'):
      takeElement_expr = res.register(self.takeElement_expr())
      if res.error: return res
      return res.success(takeElement_expr)

    elif tok.matches(TT_KEYWORD, 'lenStr'):
      lenStr_expr = res.register(self.lenStr_expr())
      if res.error: return res
      return res.success(lenStr_expr)

    elif tok.matches(TT_KEYWORD, 'Shuffle'):
      Shuffle_expr = res.register(self.Shuffle_expr())
      if res.error: return res
      return res.success(Shuffle_expr)

    elif tok.matches(TT_KEYWORD, 'system'):
      system_expr = res.register(self.system_expr())
      if res.error: return res
      return res.success(system_expr)

    elif tok.matches(TT_KEYWORD, 'sleep'):
      sleep_expr = res.register(self.sleep_expr())
      if res.error: return res
      return res.success(sleep_expr)

    elif tok.matches(TT_KEYWORD, 'while'):
      while_expr = res.register(self.while_expr())
      if res.error: return res
      return res.success(while_expr)

    elif tok.matches(TT_KEYWORD, 'func'):
      func_def = res.register(self.func_def())
      if res.error: return res
      return res.success(func_def)

    return res.failure(InvalidSyntaxError(
      tok.pos_start, tok.pos_end,
      "Expected int, float, identifier, '+', '-', '(', '[', if', 'for', 'while', 'func'"
    ))

  def list_expr(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_RSQUARE:
      res.register_advancement()
      self.advance()
    else:
      element_nodes.append(res.register(self.expr()))
      if res.error:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ']', 'var', 'if', 'for', 'while', 'func', int, float, identifier, '+', '-', '(', '[' or 'not'"
        ))

      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

      if self.current_tok.type != TT_RSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ']'"
        ))

      res.register_advancement()
      self.advance()

    return res.success(ListNode(
      element_nodes,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  def if_expr(self):
    res = ParseResult()
    all_cases = res.register(self.if_expr_cases('if'))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  def if_expr_b(self):
    return self.if_expr_cases('elif')
    
  def if_expr_c(self):
    res = ParseResult()
    else_case = None

    if self.current_tok.matches(TT_KEYWORD, 'else'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type == TT_NEWLINE:
        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        if self.current_tok.matches(TT_KEYWORD, 'end'):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'end'"
          ))
      else:
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  def if_expr_b_or_c(self):
    res = ParseResult()
    cases, else_case = [], None

    if self.current_tok.matches(TT_KEYWORD, 'elif'):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else:
      else_case = res.register(self.if_expr_c())
      if res.error: return res
    
    return res.success((cases, else_case))

  def if_expr_cases(self, case_keyword):
    res = ParseResult()
    cases = []
    else_case = None

    if not self.current_tok.matches(TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '{case_keyword}'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      if self.current_tok.matches(TT_KEYWORD, 'end'):
        res.register_advancement()
        self.advance()
      else:
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else:
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)

    return res.success((cases, else_case))
  
  def sleep_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'sleep'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'sleep'"
      ))
    
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      if self.current_tok.type != TT_INT:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'int'"
        ))

    time_sleep_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()

    body = res.register(self.statement())
    if res.error: return res

    return res.success(SleepNode(time_sleep_tok, body, False))

  def system_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'system'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'system'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      if self.current_tok.type != TT_STRING:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'string'"
        ))

    system_command_name_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()

    body = res.register(self.statement())
    if res.error: return res

    return res.success(SystemNode(system_command_name_tok, body, False))   

  def argv_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'Argv'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'Argv'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_INT:
      if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'integer or identifier'"
        ))

    argv_count_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()

    # if self.current_tok.matches != TT_RSQUARE:
    #   return res.failure(InvalidSyntaxError(
    #     self.current_tok.pos_start, self.current_tok.pos_end,
    #     f"Expected ']'"
    #   ))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(ArgvNode(argv_count_tok, body, False))

  def make_float_expr(self):
    res = ParseResult()
    if not self.current_tok.matches(TT_KEYWORD, 'make_float'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'make_float'"
      ))

    res.register_advancement()
    self.advance()  

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.matches != TT_INT:
      if self.current_tok.matches != TT_STRING:
        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected 'int or string or identifier'"
          ))

    float_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()  

    body = res.register(self.statement())
    if res.error: return res

    return res.success(MakeFloatNode(float_tok, body, False))


  def make_int_expr(self):
    res = ParseResult()
    if not self.current_tok.matches(TT_KEYWORD, 'make_int'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'make_int'"
      ))

    res.register_advancement()
    self.advance()  

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.matches != TT_FLOAT:
      if self.current_tok.matches != TT_STRING:
        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected 'int or float or identifier'"
          ))

    int_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()  

    body = res.register(self.statement())
    if res.error: return res

    return res.success(MakeIntNode(int_tok, body, False))

  def make_str_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'make_str'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'make_str'"
      ))

    res.register_advancement()
    self.advance()  

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_INT:
      if self.current_tok.matches != TT_FLOAT:
        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected 'int or float or identifier'"
          ))

    string_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()  

    body = res.register(self.statement())
    if res.error: return res

    return res.success(MakeStrNode(string_tok, body, False))


  def Exit_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'Exit'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'Exit'"
      ))

    res.register_advancement()
    self.advance()  

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_INT:
      if self.current_tok.type != TT_STRING:
        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected 'int or string or identifier'"
          ))

    exit_code_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()  

    body = res.register(self.statement())
    if res.error: return res

    return res.success(ExitNode(exit_code_tok, body, False))

  def include_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'include'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'include'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_STRING:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'string'"
      ))

    include_name_tok = res.register(self.expr())
    if res.error: return res
    res.register_advancement()
    self.advance()

    # if self.current_tok.type != TT_RPAREN:
    #   return res.failure(InvalidSyntaxError(
    #     self.current_tok.pos_start, self.current_tok.pos_end,
    #     f"Expected ')'"
    #   ))

    # res.register_advancement()
    # self.advance()
    body = res.register(self.statement())
    if res.error: return res

    return res.success(IncludeNode(include_name_tok, body, False))

  def Shuffle_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'Shuffle'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'Shuffle'"
      ))
    
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))
    
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'identifier'"
      ))    
        
    first_value = res.register(self.expr())
    if res.error: return res  
    res.register_advancement()
    self.advance() 
  
    body = res.register(self.statement())
    if res.error: return res

    return res.success(ShuffleNode(first_value, body, False))    

  def lenStr_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'lenStr'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'lenStr'"
      ))

    res.register_advancement()
    self.advance()   
    
    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      if self.current_tok.type != TT_STRING:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'string' or identifier'"
        ))    
        
    str_name = res.register(self.expr())
    if res.error: return res  
    res.register_advancement()
    self.advance() 

    body = res.register(self.statement())
    if res.error: return res

    return res.success(lenStrNode(str_name, body, False))

  def takeElement_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'takeElement'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'takeElement'"
      ))

    res.register_advancement()
    self.advance()   
    
    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'identifier'"
      ))    
        
    first_value = res.register(self.expr())
    if res.error: return res  
    res.register_advancement()
    self.advance() 

    if self.current_tok.type != TT_INT:
      if self.current_tok.type != TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'int' or 'identifier'"
        ))     
        
    second_value = res.register(self.expr())
    if res.error: return res  
    res.register_advancement()
    self.advance() 

    body = res.register(self.statement())
    if res.error: return res

    return res.success(takeElementNode(first_value, second_value, body, False))

  def randInt_expr(self): 
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'randInt'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'randInt'"
      ))

    res.register_advancement()
    self.advance()   
    
    if self.current_tok.type != TT_LPAREN:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '('"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_INT:
      if self.current_tok.type != TT_IDENTIFIER:
        if self.current_tok.type != TT_FLOAT:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected 'int' or 'float' or 'identifier'"
          ))    
        
    first_value = res.register(self.expr())
    if res.error: return res  
    res.register_advancement()
    self.advance() 

    if self.current_tok.type != TT_INT:
      if self.current_tok.type != TT_IDENTIFIER:
        if self.current_tok.type != TT_FLOAT:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected 'int' or 'float' or 'identifier'"
          ))     
        
    second_value = res.register(self.expr())
    if res.error: return res  
    res.register_advancement()
    self.advance() 

    body = res.register(self.statement())
    if res.error: return res

    return res.success(randIntNode(first_value, second_value, body, False))

  def for_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'for'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'FOR'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected identifier"
      ))

    var_name = self.current_tok
    res.register_advancement()
    self.advance()

    if self.current_tok.type != TT_EQ:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '='"
      ))

    res.register_advancement()
    self.advance()
    start_value = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'to'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'TO'"
      ))
    
    res.register_advancement()
    self.advance()

    end_value = res.register(self.expr())
    if res.error: return res

    if self.current_tok.matches(TT_KEYWORD, 'step'):
      res.register_advancement()
      self.advance()

      step_value = res.register(self.expr())
      if res.error: return res
    else:
      step_value = None

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'THEN'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'end'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'end'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

  def while_expr(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'while'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'while'"
      ))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'then'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'then'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_tok.matches(TT_KEYWORD, 'end'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'end'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))
    
    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))

  def func_def(self):
    res = ParseResult()

    if not self.current_tok.matches(TT_KEYWORD, 'func'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'func'"
      ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_IDENTIFIER:
      var_name_tok = self.current_tok
      res.register_advancement()
      self.advance()
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '('"
        ))
    else:
      var_name_tok = None
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or '('"
        ))
    
    res.register_advancement()
    self.advance()
    arg_name_toks = []

    if self.current_tok.type == TT_IDENTIFIER:
      arg_name_toks.append(self.current_tok)
      res.register_advancement()
      self.advance()
      
      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier"
          ))

        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()
      
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ')'"
        ))
    else:
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or ')'"
        ))

    res.register_advancement()
    self.advance()

    if self.current_tok.type == TT_ARROW:
      res.register_advancement()
      self.advance()

      body = res.register(self.expr())
      if res.error: return res

      return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        True
      ))
    
    if self.current_tok.type != TT_NEWLINE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '->' or NEWLINE"
      ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_tok.matches(TT_KEYWORD, 'end'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'end'"
      ))

    res.register_advancement()
    self.advance()
    
    return res.success(FuncDefNode(
      var_name_tok,
      arg_name_toks,
      body,
      False
    ))

  def bin_op(self, func_a, ops, func_b=None):
    if func_b == None:
      func_b = func_a
    
    res = ParseResult()
    left = res.register(func_a())
    if res.error: return res

    while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()
      right = res.register(func_b())
      if res.error: return res
      left = BinOpNode(left, op_tok, right)

    return res.success(left)

class RTResult:
  def __init__(self):
    self.reset()

  def reset(self):
    self.value = None
    self.error = None
    self.func_return_value = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def register(self, res):
    self.error = res.error
    self.func_return_value = res.func_return_value
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  def success(self, value):
    self.reset()
    self.value = value
    return self

  def success_return(self, value):
    self.reset()
    self.func_return_value = value
    return self
  
  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  def failure(self, error):
    self.reset()
    self.error = error
    return self

  def should_return(self):
    return (
      self.error or
      self.func_return_value or
      self.loop_should_continue or
      self.loop_should_break
    )

class Value:
  def __init__(self):
    self.set_pos()
    self.set_context()

  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context=None):
    self.context = context
    return self

  def added_to(self, other):
    return None, self.illegal_operation(other)

  def subbed_by(self, other):
    return None, self.illegal_operation(other)

  def multed_by(self, other):
    return None, self.illegal_operation(other)

  def dived_by(self, other):
    return None, self.illegal_operation(other)

  def powed_by(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_eq(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_ne(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lte(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gte(self, other):
    return None, self.illegal_operation(other)

  def anded_by(self, other):
    return None, self.illegal_operation(other)

  def ored_by(self, other):
    return None, self.illegal_operation(other)

  def notted(self, other):
    return None, self.illegal_operation(other)

  def execute(self, args):
    return RTResult().failure(self.illegal_operation())

  def copy(self):
    raise Exception('No copy method defined')

  def is_true(self):
    return False

  def illegal_operation(self, other=None):
    if not other: other = self
    return RTError(
      self.pos_start, other.pos_end,
      'Illegal operation',
      self.context
    )

class Number(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def subbed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def moded_by(self, other):
    if isinstance(other, Number):
      return Number(self.value % other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Number(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def powed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_ne(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    elif isinstance(other, TT_IDENTIFIER):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      print("btw comparing floats is not implemented yet")
      return None, Value.illegal_operation(self, other)

  def get_comparison_lt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_lte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_gte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def anded_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def ored_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None

  def copy(self):
    copy = Number(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def is_true(self):
    return self.value != 0

  def __str__(self):
    return str(self.value)
  
  def __repr__(self):
    return str(self.value)

Number.null = Number("\n")
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)

class String(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)
      
  def multed_by(self, other):
    if isinstance(other, Number):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def get_comparison_eq(self, other):
    if isinstance(other, String):
      return String(self.value == other.value).set_context(self.context), None
    elif isinstance(other, TT_IDENTIFIER):
      return String(self.value == other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def is_true(self):
    # if there is a issue in the future just un-comment the code and comment the other code
    
    # return len(self.value) > 0
    return self.value > 0

  def copy(self):
    copy = String(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return self.value

  def __repr__(self):
    return f'"{self.value}"'

class List(Value):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

  def added_to(self, other):
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None

  def subbed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be removed from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  def multed_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)
  
  def moded_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)

  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)
  
  def copy(self):
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __str__(self):
    return ", ".join([str(x) for x in self.elements])

  def __repr__(self):
    return f'[{", ".join([repr(x) for x in self.elements])}]'

class BaseFunction(Value):
  def __init__(self, name):
    super().__init__()
    self.name = name or "<anonymous>"

  def generate_new_context(self):
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
    return new_context

  def check_args(self, arg_names, args):
    res = RTResult()

    if len(args) > len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(args) - len(arg_names)} too many args passed into {self}",
        self.context
      ))
    
    if len(args) < len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(arg_names) - len(args)} too few args passed into {self}",
        self.context
      ))

    return res.success(None)

  def populate_args(self, arg_names, args, exec_ctx):
    for i in range(len(args)):
      arg_name = arg_names[i]
      arg_value = args[i]
      arg_value.set_context(exec_ctx)
      exec_ctx.symbol_table.set(arg_name, arg_value)

  def check_and_populate_args(self, arg_names, args, exec_ctx):
    res = RTResult()
    res.register(self.check_args(arg_names, args))
    if res.should_return(): return res
    self.populate_args(arg_names, args, exec_ctx)
    return res.success(None)

class Function(BaseFunction):
  def __init__(self, name, body_node, arg_names, should_auto_return):
    super().__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_auto_return = should_auto_return

  def execute(self, args):
    res = RTResult()
    interpreter = Interpreter() 
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_return_value == None: return res

    ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
    return res.success(ret_value)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = RTResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)
  
  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"


  def execute_print(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return RTResult().success(Number.null)
  execute_print.arg_names = ['value']
  
  def execute_print_ret(self, exec_ctx):
    return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
  execute_print_ret.arg_names = ['value']
  
  def execute_input(self, exec_ctx):
    text = input()
    return RTResult().success(String(text))
  execute_input.arg_names = []

  def execute_input_int(self, exec_ctx):
    text = input()
    try:
      number = int(text)
    except ValueError as e:
      print(e)
      exit(1)
    return RTResult().success(Number(number))
  execute_input_int.arg_names = []

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'clear') 
    return RTResult().success(Number.null)
  execute_clear.arg_names = []

  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_function.arg_names = ["value"]

  def execute_append(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    value = exec_ctx.symbol_table.get("value")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    list_.elements.append(value)
    return RTResult().success(Number.null)
  execute_append.arg_names = ["list", "value"]

  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be number",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RTResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_table.get("listA")
    listB = exec_ctx.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RTResult().success(Number.null)
  execute_extend.arg_names = ["listA", "listB"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be list",
        exec_ctx
      ))
      
    return RTResult().success(Number(len(list_.elements)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be string",
        exec_ctx
      ))

    fn = fn.value

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)
    
    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))

    return RTResult().success(Number.null)
  execute_run.arg_names = ["fn"]

BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len					= BuiltInFunction("len")
BuiltInFunction.run					= BuiltInFunction("run")

class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None

class SymbolTable:
  def __init__(self, parent=None):
    self.symbols = {}
    self.parent = parent

  def get(self, name):
    value = self.symbols.get(name, None)
    if value == None and self.parent:
      return self.parent.get(name)
    return value

  def set(self, name, value):
    self.symbols[name] = value

  def remove(self, name):
    del self.symbols[name]


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number.null)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("math_pi", Number.math_PI)
global_symbol_table.set("printh", BuiltInFunction.print)
global_symbol_table.set("printh_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_number", BuiltInFunction.is_number)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_function", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("entend", BuiltInFunction.extend)
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)

def cmd_echoed(cmd):
    print("[CMD] %s" % " ".join(map(shlex.quote, cmd)))
    subprocess.call(cmd)

def generate_output(basepath, hustle_ext):
  if basepath.endswith(hustle_ext):
      basepath = basepath[:-len(hustle_ext)]
  print("[INFO] Generating %s" % (basepath + ".asm"))
  cmd_echoed(["nasm", "-felf64", basepath + ".asm"])
  cmd_echoed(["ld", "-o", basepath, basepath + ".o"])

def run_compiled_code(basepath, hustle_ext):
  if basepath.endswith(hustle_ext):
      basepath = basepath[:-len(hustle_ext)]
  # not native yet
  print("[INFO] Running %s" % (basepath)) 
  cmd_echoed(["./"+basepath])

# globals lists
tokens = []
num_stack = []

com_symbols = {

}

varnames = []
extern_varnames = []
cached_string_id = []

# COMPILATION MODE IS STILL IN PROGRESS AND NOT COMPLETE (USE IT AT YOUR OWN RISK)
class CompileCode:
  def __init__(self, parse_idx=0, lex_idx=0):
    # use this to keep track of the position in the file
    self.parse_idx = parse_idx
    self.lex_idx   = lex_idx

  def read_program(self, basename):
    with open(basename, "r") as ip:
      program = ip.read()
      program += "<EOF>"
      ip.close() 
    return program

  #TODO: check for all intrintics and builtInFuctions (if-else logic)
  #TODO: make a new parser and lexer for compilation of code
  def generate_nasm_x84_assembly(self, basename, hustle_ext, basepath, tokens):
    basepath = self.endswith1(hustle_ext, basepath)
    program = self.read_program(basename)
    with open(basepath+".asm", "w") as o:
      # TODO: unhardcode this
      o.write("global _start\n")
      o.write("section .text\n")
      o.write("_start:\n")

      toks = self.lex(program)
      self.parse(toks, o, program)

      o.write( "section .text\n")
      o.write( "    mov    rax, 60                  ; system call for exit\n") 
      o.write( "    mov    rdi, 0                   ; exit code 0\n")
      o.write( "    syscall\n")

    generate_output(basepath, hustle_ext)
  # TODO: Re-write the parser and the lexer for compilation mode make it more robust cause this one is shit
  def parse(self, toks, asm, data):
    i = 0
    data = list(data)
    for char in data:
      if char == "\n":
        self.parse_idx += 1
    # FIXME: this is a hack to get the <EOF> also counted in the line counter for the parser
    self.parse_idx += 1 
    
    #TODO: implement more intrinsics and builtInFunctions (if-else logic)
    while(i < len(toks)):
      # TODO: add number evaluation without eval() function 
      try:
        if toks[i] + " " + toks[i+1][0:6] == "PRINTH STRING" or toks[i] + " " + toks[i+1][0:3] == "PRINTH NUM" or toks[i] + " " + toks[i+1][0:4] == "PRINTH EXPR" or toks[i] + " " + toks[i+1][0:3] == "PRINTH VAR":
          if toks[i+1][0:6] == "STRING":
            message = toks[i+1][7:]  
            message = message
            # TODO: implement better escape sequence handling
            # TODO: first check for \n and \t in the lexer and do not allow any other escape sequence in the string for now
            message = message[1:-1]
            # for now just use backticks and let nasm handle escape sequences
            message = "`" + message + "`"
            # FIXME: this is a very buggy code, as there is a probabilty of getting the same random number twice
            message_id = str(random.randint(0, 1000000))
            if message_id in cached_string_id: 
              message_id = str(random.randint(1000001, 100000000))
            cached_string_id.append(message_id)
            message_id = "string" + message_id
            asm.write( "section .text\n")
            asm.write( "    mov    rax, 1                     ; sys call for write\n")
            asm.write( "    mov    rdi, 1                     ; file handle 1 is stdout\n")
            asm.write(f"    mov    rsi, {message_id}               ; ardress of string to output\n")
            asm.write(f"    mov    rdx, {len(message)-3}                    ; numbers of bytes for the memory of the string\n")
            asm.write( "    syscall                           ; invoke the os to do the write\n")
            asm.write( "    section     .data\n")
            asm.write(f"{message_id}: db     {message}\n")
          elif toks[i+1][0:3] == "NUM":
            message = toks[i+1][4:]  
            message = "\""+message+"\""
            asm.write( "section .text\n")
            asm.write( "    mov    rax, 1                     ; sys call for write\n")
            asm.write( "    mov    rdi, 1                     ; file handle 1 is stdout\n")
            asm.write( "    mov    rsi, message               ; ardress of string to output\n")
            asm.write(f"    mov    rdx, {len(message)-2}                    ; numbers of bytes for the memory of the string\n")
            asm.write( "    syscall                           ; invoke the os to do the write\n")
            asm.write( "    section     .data\n")
            asm.write(f"message: db     {message}, 10         ; note the newline at the end\n")

          elif toks[i+1][0:4] == "EXPR":
            message = toks[i+1][5:]  
            message = self.evalExpr(message)
            message = ("\""+message+"\"")
            asm.write( "section .text\n")
            asm.write( "    mov    rax, 1                     ; syscall for write\n")
            asm.write( "    mov    rdi, 1                     ; file handle 1 is stdout\n")
            asm.write( "    mov    rsi, message               ; ardress of string to output\n")
            asm.write(f"    mov    rdx, {len(message)-2}                    ; numbers of bytes for the memory of the string\n")
            asm.write( "    syscall                           ; invoke the os to do the write\n")
            asm.write( "    section     .data\n")
            asm.write(f"message: db     {message}, 10         ; note the newline at the end\n")
          elif toks[i+1][0:3] == "VAR":
            current_var_name = toks[i+1]
            current_var_name = current_var_name[4:]
            current_var_value = com_symbols[current_var_name]
            if current_var_value[0:6] == "STRING":
              current_var_value = current_var_value[7:]
            elif current_var_value[0:3] == "NUM":
              current_var_value = current_var_value[4:]
              current_var_value = "\""+current_var_value+"\""
            elif current_var_value[0:4] == "EXPR":
              current_var_value = self.evalExpr(current_var_value[5:])
              current_var_value = ("\""+current_var_value+"\"")
            else:
              print("ERROR: invalid variable type")
            # TODO: check if the variable is not define if yes then throw an error
            # TODO: check if the variable is reference before assignement if yes then throw an error
            # TODO: check if the printh intrinsic is calling a undifined variable if yes throw an error
            if current_var_name in varnames:
              asm.write("section .text\n")
              asm.write( "    mov rax, 1                        ; syscall for write\n")
              asm.write( "    mov rdi, 1                        ; file handle 1 is stdout\n")
              asm.write(f"    mov rsi, {str(current_var_name)}                       ; ardress of the string to output\n")
              asm.write(f"    mov rdx, {len(current_var_value)-2}                      ; numbers of bytes for the memory of the variable value\n")
              asm.write( "    syscall                           ; invoke the operating system to do a write\n")              
            else:
              print("ERROR: undefined reference to variable " + current_var_name)
              exit(1)
          i += 2 
        elif toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:6] == "VAR EQUALS STRING" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:3] == "VAR EQUALS NUM" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:4] == "VAR EQUALS EXPR":
          varname = toks[i][4:]
          if toks[i+2][0:6] == "STRING":
            varvalue = toks[i+2][7:]
            varvalue = varvalue[1:-1]
            varvalue = "`" + varvalue + "`"
          elif toks[i+2][0:3] == "NUM":
            varvalue = toks[i+2][4:]
          elif toks[i+2][0:4] == "EXPR":
            varvalue = toks[i+2][5:]

          if toks[i+2][0:6] == "STRING":
            self.assign_var(toks[i], toks[i+2])
            asm.write( "    section .data\n")
            asm.write(f"{varname}: db    {varvalue}         ; hardcoded newlines as newlines not supported yet\n")
          elif toks[i+2][0:3] == "NUM":
            varvalue = ("\""+varvalue+"\"")
            self.assign_var(toks[i], toks[i+2])
            asm.write( "    section .data\n")
            asm.write(f"{varname}: db    {varvalue}, 10         ; hardcoded newlines as newlines not supported yet\n")
          elif toks[i+2][0:4] == "EXPR":
            evaledValue = self.evalExpr(varvalue)
            self.assign_var(toks[i], "NUM:"+evaledValue)
            evaledValue = ("\""+evaledValue+"\"")
            asm.write( "    section .data\n")
            asm.write(f"{varname}: db    {evaledValue}, 10         ; hardcoded newlines as newlines not supported yet\n")
          else:
            print("ERROR: invalid assignment of variable at line %s" % str(self.parse_idx)) 
            exit(1)

          if varname in varnames:
            print("ERROR: Redefination of variable at line %s" % str(self.parse_idx))
            print("ERROR: variable name cannot contain digits for now")
            print("ERROR: variable name: %s" % str(varname))
            exit(1)

          varnames.append(varname)
          i += 3
        else:
          print("ERROR: Unknown intrinsic or BuiltInFunction: %s" % toks[i])
          exit(1)
      except Exception as e:
        # TODO: implement typechecking and unhardcode this error
        if str(e) == "list index out of range":
          print("TODO: implement typechecking")
          print("error at line: %s" % str(self.parse_idx))
          print("ERROR: %s\n" % e)
          exit(1)
        else:
          print(str(e))
          exit(1)

  # THE COMPILER MODE OF THIS LEXER HAS NO SUPPORT FOR COMMENTS YET
  def lex(self, data):
    tok = ""
    data = list(data)
    isexpr = 0
    string = ""
    state = 0
    expr = ""
    eof = 0
    varname = ""
    varstarted = 0
    for char in data:
      eof += 1
      tok += char
      if tok == " ":
        if state == 0:
          tok = ""
        else:
          tok = " "
      elif tok == "\n" or tok == "<EOF>":
        self.lex_idx += 1
        if expr != "" and isexpr == 1 and state != 1:
          self.make_Expr(expr)
          expr = ""
          isexpr = 0
        elif expr != "" and isexpr == 0 and state != 1:
          self.make_Number(expr)
          expr = ""
        elif varname != "":
          self.make_Var(varname)
          varname = ""
          varstarted = 0
        tok = ""
      elif tok in DIGITS:
        if state == 0:
          expr += tok
          tok = ""
      elif tok == "=" and state == 0:
        if varname != "":
          self.make_Var(varname)
          varname = ""
          varstarted = 0
        self.make_Equals()
        tok = ""
      elif tok == "var" and state == 0:
        varstarted = 1
        varname += tok
        varname = varname[6:]
        tok = ""
      elif tok in extern_varnames and state == 0:
          tokens.append("VAR:"+tok)
          tok = ""
      elif varstarted == 1:
        if tok == "<" or tok == ">":
          if varname != "":
            self.make_Var(varname)
            varname = ""
            varstarted = 0
        varname += tok
        tok = ""
      elif tok == "printh":
        self.printh_intrinsic()
        tok = ""
      elif tok == "+" or tok == "-" or tok == "*" or tok == "/" or tok == "%": # TODO: implement priority system using brackets
        if state != 1:
          expr += tok 
          isexpr = 1
          tok = ""
        else:
          string += tok
          isexpr = 0
          tok = ""
      elif tok == "(": # TODO: implement left perenthesis for precedence
        # if isexpr == 1:
        #   expr += tok
        #   tok = ""
        #   isexpr = 0
        # else: 
        tok = ""
      elif tok == ")": # TODO: implement right perenthesis for precedence
        # if isexpr == 1:
        #   expr += tok
        #   tok = ""
        #   isexpr = 0
        # else: 
        tok = ""
      elif tok == "\"":
        if state == 0:
          state = 1
        elif state == 1:
          self.makeString_intrinsic(string)
          string = ""
          state = 0
          tok = ""
      if state == 1:
        string += tok
        tok = ""
    #print(tokens)
    #return ''
    return tokens 
  
  def make_Equals(self):
    tokens.append("EQUALS")

  def assign_var(self, varname, varvalue):
    com_symbols[varname[4:]] = varvalue

  def make_Var(self, varname):
    tokens.append(("VAR:" + varname))
    extern_varnames.append(varname)

  def make_Expr(self, expr):
    tokens.append("EXPR:" + expr)
  
  def make_Number(self, num):
    tokens.append("NUM:" + num)

  def makeString_intrinsic(self, string):
    tokens.append("STRING:" + string + "\"")

  def printh_intrinsic(self):
    tokens.append("PRINTH")

  def evalExpr(self, expr):
    # I know what I am doing wrong here
    # the eval function is not safe to use
    # but before you can input malicious code, the lexer will give you a error
    # I will make my own evalExpr function later 
    # this is cheating a little as this is a python's built in function and not a assembly code of doing this but for now this works fine
    return str(eval(expr))

  def endswith1(self, hustle_ext, basepath):
    if basepath.endswith(hustle_ext):
        basepath = basepath[:-len(hustle_ext)]
    return basepath

  # TODO: make functions for almost all intrinsics and builtInFunctions    

def com_run(fn, text, data):
  lexer = Lexer(fn, text)
  tokens, error1 = lexer.make_tokens()
  if error1: return None, error1

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  basename = path.basename(data)
  basedir = path.dirname(data)
  basepath = path.join(basedir, basename)

  compiler = CompileCode(0, 0)
  error = compiler.generate_nasm_x84_assembly(basepath, ".hsle", basepath, tokens)

  if error:
    print(error)

def run(fn, text):
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error

class Interpreter:
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')


  def visit_NumberNode(self, node, context):
    return RTResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_StringNode(self, node, context):
    return RTResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
  )

  def visit_ListNode(self, node, context):
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RTError(
        node.pos_start, node.pos_end,
        f"'{var_name}' is not defined",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  def visit_VarAssignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinOpNode(self, node, context):
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    if node.op_tok.type == TT_PLUS:
      result, error = left.added_to(right)
    elif node.op_tok.type == TT_MINUS:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == TT_MUL:
      result, error = left.multed_by(right)
    elif node.op_tok.type == TT_MOD:
      result, error = left.moded_by(right)
    elif node.op_tok.type == TT_DIV:
      result, error = left.dived_by(right)
    elif node.op_tok.type == TT_POW:
      result, error = left.powed_by(right)
    elif node.op_tok.type == TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(TT_KEYWORD, 'and'):
      result, error = left.anded_by(right)
    elif node.op_tok.matches(TT_KEYWORD, 'or'):
      result, error = left.ored_by(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  def visit_UnaryOpNode(self, node, context):
    res = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    if node.op_tok.type == TT_MINUS:
      number, error = number.multed_by(Number(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'not'):
      number, error = number.notted()

    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  def visit_IfNode(self, node, context):
    res = RTResult()

    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Number.null if should_return_null else expr_value)

    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Number.null if should_return_null else expr_value)

    return res.success(Number.null)

  def visit_ArgvNode(self, node, context):
    res = RTResult()
    argvs = []

    argv_count = res.register(self.visit(node.argv_count, context))
    if res.should_return(): return res
   
    # I think this is how argv work in python
    # ./hustle argv0 argv1 argv2 argv3 argv4 .....

    # Context:-
    # ./hustle  run   file  

    def main():
    # I am adding 2 because the code runner uses 2 args to interpret a file
    # 1 is run subcommand
    # other is the file itself
    # so following my concept of how argvs work in python 
    # I added 2 args from 0 to subtract the offset 
      rs = sys.argv[int(str(int(str(argv_count)) + 2))] 
      argvs.append(rs)

    main()
    return res.success(
      Number.null if node.should_return_null else
      List(argvs).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ExitNode(self, node, context):
    res = RTResult()
    exits = []

    exit_code = res.register(self.visit(node.exit_code, context))
    if res.should_return(): return res

    def main():
      try:
        try:
          if isinstance(int(str(exit_code)), int): 
            exit(int(str(exit_code)))
          else: 
            exit()
        except Exception as e: 
          if isinstance(str(exit_code), str): 
            exit(str(exit_code))
      except Exception as e: 
        print("Runtime Error: " + str(e))
    main()
    return res.success(
      Number.null if node.should_return_null else
      List(exits).set_context(context).set_pos(node.pos_start, node.pos_end)
    )    

  def visit_MakeFloatNode(self, node, context):
    res = RTResult()
    float_name = res.register(self.visit(node.float_tok, context))
    if res.should_return(): return res

    flootes = float(str(float_name))

    return res.success(
      Number.null if node.should_return_null else
      Number(flootes).set_context(context).set_pos(node.pos_start, node.pos_end)
    )    

  def visit_MakeIntNode(self, node, context):
    res = RTResult()
    int_name = res.register(self.visit(node.int_tok, context))
    if res.should_return(): return res

    ant = int(str(int_name))

    return res.success(
      Number.null if node.should_return_null else
      Number(ant).set_context(context).set_pos(node.pos_start, node.pos_end)
    )    

  def visit_MakeStrNode(self, node, context):
    res = RTResult()
    str_name = res.register(self.visit(node.string_tok, context))
    if res.should_return(): return res

    strang = str(str_name)

    return res.success(
      Number.null if node.should_return_null else
      String(strang).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_IncludeNode(self, node, context):
    res = RTResult()
    modules = {
      "@" : "stdlib.hsle"
    }
    include_var = res.register(self.visit(node.include_name, context))
    if res.should_return(): return res    
    
    def open_file(filename):
      if filename.endswith('.hsle'):
        data = filename
        return data
      else:
        print("file does not have .hsle extension")
        exit(1)

    if str(include_var) == "all":
      data = open_file(modules["@"])
    elif str(include_var) == "stdlib":
      data = open_file(modules["@"])
    else: 
      try: 
        data = open_file(str(include_var)) 
      except:
        print("RUNTIME ERROR: could not find module")
        print("please give relative path or the full path to the module")
        sys.exit("File Not Found: " + str(include_var))
        
    text = "run(\""+data+"\")"
    result, error = run('<stdin>',text)

    if error:
      print(error.as_string())
    elif result:
      if len(result.elements) == 1:
        print(repr(result.elements[0]))
      else:
        print(repr(result))
          
    return res.success(
      Number.null if node.should_return_null else
      List(modules).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_SleepNode(self, node, context): 
    res = RTResult()
    times = []

    sleep_value = res.register(self.visit(node.time_name, context))
    if res.should_return(): return res   

    if float(str(sleep_value)) <= 0:
      print("RUNTIME ERROR: sleep value is negative or null")
      print("time cannot sleep for " + sleep_value + " seconds")
      sys.exit("Syntax Error: Incorrect Syntax " + str(sleep_value))
    else:
      time.sleep(float(str(sleep_value)))

    return res.success(
      Number.null if node.should_return_null else
      List(times).set_context(context).set_pos(node.pos_start, node.pos_end)
    )      

  def visit_SystemNode(self, node, context):
    res = RTResult()
    commands = []

    command_value = res.register(self.visit(node.system_command_name, context))
    if res.should_return(): return res   

    def crun():
      try:
        os.system(str(command_value))
      except: 
        print("Syntax Error: Invalid command in system keyword")
        sys.exit("Invalid Command: " + command_value)
      
    crun()
    
    return res.success(
      Number.null if node.should_return_null else
      List(commands).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ShuffleNode(self, node, context):
    res = RTResult()

    shuffle_value = res.register(self.visit(node.list_name, context))
    if res.should_return(): return res

    # TODO: implement a shuffle function that shuffles a list
    if isinstance(shuffle_value, List):
      list_name = shuffle_value.elements
      random.shuffle(list_name)
    else:
      print("RUNTIME ERROR: shuffle value is not a list")
      print("make sure the value is a list")
      sys.exit("Syntax Error: Incorrect Syntax " + str(shuffle_value))

    return res.success(
      Number.null if node.should_return_null else
      # convert this back to List() when you implemented the shuffle function
      List(list_name).set_context(context).set_pos(node.pos_start, node.pos_end)
    )    

  def visit_lenStrNode(self, node, context):
    res = RTResult()

    str_tok = res.register(self.visit(node.string_tok, context))
    if res.should_return(): return res

    try:
      length = len(str(str_tok))
    except Exception as e:
      print("RUNTIME ERROR: " + e)
      sys.exit("RUNTIME Error: could not take the length of the string " + str(str_tok))

    return res.success(
      Number.null if node.should_return_null else
      Number(length).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_takeElementNode(self, node, context):
    res = RTResult()
    lses = []

    list_name = res.register(self.visit(node.list_name, context))
    if res.should_return(): return res 

    index = res.register(self.visit(node.index_name, context))
    if res.should_return(): return res

    # github copilot helped me out on this one lul
    def take_element(list_name, index):
      if isinstance(list_name, List):
        if isinstance(index, Number):
          if index.value < len(list_name.elements):
            return list_name.elements[index.value]
          else:
            print("RUNTIME ERROR: index out of range")
            sys.exit("Index Out of Range: " + str(index.value))
        else:
          print("RUNTIME ERROR: index is not a number")
          sys.exit("Index is not a number: " + str(index))
      # check if the list is a string
      elif isinstance(list_name, String):
        if isinstance(index, Number):
          if index.value < len(list_name.value):
            return String(list_name.value[index.value])
          else:
            print("RUNTIME ERROR: index out of range")
            sys.exit("Index Out of Range: " + str(index.value))
        else:
          print("RUNTIME ERROR: index is not a number")
          sys.exit("Index is not a number: " + str(index))
      else:
        print("RUNTIME ERROR: list is not a list or string")
        sys.exit("List is not a list or string: " + str(list_name))
    lses.append(take_element(list_name, index))

    try:
      take_element(list_name, index)
    except Exception as e:
      print("RUNTIME ERROR: " + str(e))

    return res.success(
      Number.null if node.should_return_null else
      List(lses).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_randIntNode(self, node, context):
    res = RTResult()
    rands = []

    min_value = res.register(self.visit(node.first_rand_name, context))
    if res.should_return(): return res 

    max_value = res.register(self.visit(node.second_rand_name, context))
    if res.should_return(): return res

    try:
      num = random.randint(int(str(min_value)), int(str(max_value)))   
    except:
      print(" : getting random numbers failed : ")
      sys.exit(1)

    return res.success(
      Number.null if node.should_return_null else
      Number(num).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ForNode(self, node, context):
    res = RTResult()
    elements = []

    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res

    end_value = res.register(self.visit(node.end_value_node, context))
    if res.should_return(): return res

    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
    else:
      step_value = Number(1)

    i = start_value.value
  

    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value
    
    while condition():
      context.symbol_table.set(node.var_name_tok.value, Number(i))
      i += step_value.value

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res
      
      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_WhileNode(self, node, context):
    res = RTResult()
    elements = []

    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      if not condition.is_true():
        break

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue
      
      if res.loop_should_break:
        break

      elements.append(value)

    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_FuncDefNode(self, node, context):
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)
    
    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node, context):
    res = RTResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  def visit_ReturnNode(self, node, context):
    res = RTResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Number.null
    
    return res.success_return(value)

  def visit_ContinueNode(self, node, context):
    return RTResult().success_continue()

  def visit_BreakNode(self, node, context):
    return RTResult().success_break()
