import re
from typing import List, Optional, Any
from .models import *

class Token:
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"

class Tokenizer:
    TOKEN_TYPES = [
        ('COMMENT', r'►.*'),
        ('STRING', r'"[^"]*"'),
        ('NUMBER', r'\d+(\.\d+)?'),
        ('ASSIGN', r'🡨|<-'), # Support both arrow char and text representation
        ('LE', r'≤|<='),
        ('GE', r'≥|>='),
        ('NE', r'≠|<>'),
        ('EQ', r'='),
        ('LT', r'<'),
        ('GT', r'>'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('DOTDOT', r'\.\.'),
        ('DOT', r'\.'),
        ('COMMA', r','),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('MULTIPLY', r'\*'),
        ('DIVIDE', r'/'),
        ('MOD', r'mod'),
        ('DIV', r'div'),
        ('CEIL', r'┌|ceil'),
        ('FLOOR', r'└|floor'), # Assuming these might be used as operators or functions
        ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]

    def __init__(self, code: str):
        self.code = code
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            match = None
            for token_type, pattern in self.TOKEN_TYPES:
                # Use word boundary for keywords/operators that are words
                if token_type in ['MOD', 'DIV']:
                    regex = re.compile(pattern + r'(?![a-zA-Z0-9_])', re.IGNORECASE)
                else:
                    regex = re.compile(pattern)
                
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    if token_type == 'NEWLINE':
                        self.line += 1
                        self.column = 1
                    elif token_type == 'SKIP':
                        self.column += len(value)
                    elif token_type == 'COMMENT':
                        # Ignore comments
                        pass
                    elif token_type == 'MISMATCH':
                        raise SyntaxError(f'Unexpected character {value!r} on line {self.line}')
                    else:
                        tokens.append(Token(token_type, value, self.line, self.column))
                        self.column += len(value)
                    
                    self.pos = match.end()
                    break
            if not match:
                 raise SyntaxError(f'Unexpected character on line {self.line}')
        
        self.tokens = tokens
        return tokens

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0) -> Optional[Token]:
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, type_: str = None) -> Token:
        token = self.peek()
        if token is None:
             raise SyntaxError("Unexpected end of input")
        if type_ and token.type != type_:
            raise SyntaxError(f"Expected {type_}, got {token.type} ('{token.value}') at line {token.line}")
        self.pos += 1
        return token

    def match(self, type_: str) -> bool:
        token = self.peek()
        if token and token.type == type_:
            self.consume()
            return True
        return False

    def parse_program(self) -> Program:
        classes = []
        procedures = []
        
        # Parse Classes
        while self.peek() and self.peek().value.lower() == 'clase':
            classes.append(self.parse_class_def())
        
        # Parse Procedures
        while self.peek() and self.peek().type == 'ID' and self.peek(1) and self.peek(1).type == 'LPAREN':
             # Heuristic to distinguish procedure definition from main block or other things
             # Actually, the grammar says "nombre_subrutina(params) begin ... end"
             # But main block is just "begin ... end" or statements?
             # The grammar implies a structure. Let's assume procedures come before the main block or are the only top level things besides classes.
             # Wait, the grammar doesn't explicitly define a "Main Program" structure, but usually there is one.
             # Let's assume if we see ID LPAREN, it's a procedure def.
             procedures.append(self.parse_procedure_def())

        # Parse Main Block (optional or implicit?)
        # If we see 'begin', it's the main block.
        main_block = Block([])
        if self.peek() and self.peek().value.lower() == 'begin':
            self.consume() # begin
            main_block = self.parse_block_body() # parses until 'end'
            self.consume('ID') # consume 'end' (the tokenizer types 'end' as ID) - wait, 'end' is ID.
            # We need to verify if 'end' is reserved. In my tokenizer ID matches keywords.
            # I should handle keywords better.
        
        return Program("Program", classes, procedures, main_block)

    def parse_class_def(self) -> ClassDef:
        self.consume('ID') # Clase
        name = self.consume('ID').value
        self.consume('LBRACE') # We need LBRACE in tokenizer!
        # Wait, grammar says "llaves".
        attributes = []
        while self.peek() and self.peek().type != 'RBRACE': # Need RBRACE
             attributes.append(self.consume('ID').value)
        self.consume('RBRACE')
        return ClassDef(name, attributes)

    def parse_procedure_def(self) -> ProcedureDef:
        name = self.consume('ID').value
        self.consume('LPAREN')
        params = []
        if self.peek().type != 'RPAREN':
            while True:
                # Parameter parsing is tricky: "param1" or "arr[n]..[m]" or "Clase obj"
                # Simplified for now:
                type_info = "Unknown"
                if self.peek().value.lower() == 'clase':
                    self.consume()
                    type_info = self.consume('ID').value # Class Name
                    param_name = self.consume('ID').value # Object Name? Grammar says "Clase nombre_objeto"
                    # Wait, usually it is "Type Name". Grammar says "Clase nombre_objeto".
                    # So param name is the second ID.
                    params.append(Parameter(param_name, type_info))
                else:
                    param_name = self.consume('ID').value
                    # Check for array dimensions
                    if self.peek().type == 'LBRACKET':
                        type_info = "Array"
                        while self.match('LBRACKET'):
                            # consume dimensions
                            while self.peek().type != 'RBRACKET':
                                self.consume()
                            self.consume('RBRACKET')
                            if self.match('DOTDOT'):
                                # Range
                                pass
                    params.append(Parameter(param_name, type_info))
                
                if not self.match('COMMA'):
                    break
        self.consume('RPAREN')
        
        self.consume_keyword('begin')
        body = self.parse_block_body()
        self.consume_keyword('end')
        
        return ProcedureDef(name, params, body)

    def parse_block_body(self) -> Block:
        statements = []
        # Parse until 'end' or 'until' or 'else' (if nested)
        # We need to know when to stop.
        # Usually blocks are terminated by 'end', 'until', 'else'.
        while self.peek():
            token = self.peek()
            val = token.value.lower()
            if val in ['end', 'until', 'else']:
                break
            statements.append(self.parse_statement())
        return Block(statements)

    def parse_statement(self) -> Statement:
        token = self.peek()
        val = token.value.lower()

        if val == 'if':
            return self.parse_if()
        elif val == 'for':
            return self.parse_for()
        elif val == 'while':
            return self.parse_while()
        elif val == 'repeat':
            return self.parse_repeat()
        elif val == 'call':
            return self.parse_call()
        elif token.type == 'ID':
            # Assignment or Procedure Call (if implicit without CALL, but grammar says CALL is used)
            # Grammar: "La asignación se indica mediante el símbolo 🡨"
            # So ID <- Expr
            return self.parse_assignment()
        else:
            raise SyntaxError(f"Unexpected token {token} at start of statement")

    def parse_assignment(self) -> Assignment:
        # target <- value
        # target could be ID, ID.field, ID[idx]
        target_expr = self.parse_expression() # We parse as expression to handle fields/arrays
        # Verify target_expr is a valid lvalue (Variable, FieldAccess, ArrayAccess)
        # For now assume it is.
        # We need to convert Expression back to string representation or keep as Node?
        # Model says target: str. Let's keep it simple for now, maybe just ID.
        # But grammar allows x.f <- y.
        # Let's change Assignment model to take Expression as target or handle it.
        # For now, let's assume target is just the string representation.
        
        if not self.match('ASSIGN'):
             raise SyntaxError(f"Expected assignment operator at line {self.peek().line}")
        
        value = self.parse_expression()
        return Assignment(str(target_expr), value) # Simplified target

    def parse_if(self) -> IfStatement:
        self.consume_keyword('if')
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        self.consume_keyword('then')
        
        # Grammar says: if (cond) then begin ... end else begin ... end
        # But also allows single statement? "begin ... end" is a block.
        # Let's assume it always uses begin/end as per grammar examples.
        self.consume_keyword('begin')
        then_block = self.parse_block_body()
        self.consume_keyword('end')
        
        else_block = None
        if self.peek() and self.peek().value.lower() == 'else':
            self.consume()
            self.consume_keyword('begin')
            else_block = self.parse_block_body()
            self.consume_keyword('end')
            
        return IfStatement(condition, then_block, else_block)

    def parse_for(self) -> ForLoop:
        self.consume_keyword('for')
        variable = self.consume('ID').value
        self.consume('ASSIGN')
        start_val = self.parse_expression()
        self.consume_keyword('to')
        end_val = self.parse_expression()
        self.consume_keyword('do')
        self.consume_keyword('begin')
        body = self.parse_block_body()
        self.consume_keyword('end')
        return ForLoop(variable, start_val, end_val, body)

    def parse_while(self) -> WhileLoop:
        self.consume_keyword('while')
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        self.consume_keyword('do')
        self.consume_keyword('begin')
        body = self.parse_block_body()
        self.consume_keyword('end')
        return WhileLoop(condition, body)

    def parse_repeat(self) -> RepeatLoop:
        self.consume_keyword('repeat')
        body = self.parse_block_body()
        self.consume_keyword('until')
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        return RepeatLoop(condition, body)

    def parse_call(self) -> Call:
        self.consume_keyword('call')
        proc_name = self.consume('ID').value
        self.consume('LPAREN')
        args = []
        if self.peek().type != 'RPAREN':
            while True:
                args.append(self.parse_expression())
                if not self.match('COMMA'):
                    break
        self.consume('RPAREN')
        return Call(proc_name, args)

    def parse_expression(self) -> Expression:
        # Simple recursive descent for expressions
        # Priority: ( ) -> * / -> + - -> Relational
        return self.parse_relational()

    def parse_relational(self) -> Expression:
        left = self.parse_term()
        while self.peek() and self.peek().type in ['LT', 'GT', 'LE', 'GE', 'EQ', 'NE']:
            op = self.consume().value
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        return left

    def parse_term(self) -> Expression:
        left = self.parse_factor()
        while self.peek() and self.peek().type in ['PLUS', 'MINUS']:
            op = self.consume().value
            right = self.parse_factor()
            left = BinaryOp(left, op, right)
        return left

    def parse_factor(self) -> Expression:
        left = self.parse_primary()
        while self.peek() and self.peek().type in ['MULTIPLY', 'DIVIDE', 'MOD', 'DIV']:
             op_token = self.consume()
             right = self.parse_primary()
             left = BinaryOp(left, op_token.value, right)
        return left

    def parse_primary(self) -> Expression:
        token = self.peek()
        if self.match('LPAREN'):
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        elif token.type == 'NUMBER':
            self.consume()
            return Literal(token.value, "Integer") # Simplified type
        elif token.type == 'STRING':
            self.consume()
            return Literal(token.value, "String")
        elif token.type == 'ID':
            # Could be Variable, ArrayAccess, FieldAccess, FunctionCall (length)
            name = self.consume().value
            expr = Variable(name)
            
            # Handle suffix: .field or [index]
            while True:
                if self.match('DOT'):
                    field = self.consume('ID').value
                    expr = FieldAccess(str(expr), field) # Simplified object name
                elif self.match('LBRACKET'):
                    index = self.parse_expression()
                    self.consume('RBRACKET')
                    expr = ArrayAccess(str(expr), index)
                else:
                    break
            return expr
        elif token.value.lower() == 'length':
             self.consume()
             self.consume('LPAREN')
             arg = self.parse_expression()
             self.consume('RPAREN')
             return UnaryOp('length', arg)
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def consume_keyword(self, keyword: str):
        token = self.peek()
        if token and token.type == 'ID' and token.value.lower() == keyword.lower():
            self.consume()
        else:
            raise SyntaxError(f"Expected keyword '{keyword}', got {token}")

