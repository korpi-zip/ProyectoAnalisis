from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ASTNode:
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for k, v in self.__dict__.items():
            if v is None:
                continue
            if isinstance(v, ASTNode):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                result[k] = v
        return result

@dataclass
class Program(ASTNode):
    name: str
    classes: List['ClassDef'] = field(default_factory=list)
    procedures: List['ProcedureDef'] = field(default_factory=list)
    main_block: 'Block' = field(default_factory=lambda: Block([]))

@dataclass
class ClassDef(ASTNode):
    name: str
    attributes: List[str]

@dataclass
class ProcedureDef(ASTNode):
    name: str
    params: List['Parameter']
    body: 'Block'

@dataclass
class Parameter(ASTNode):
    name: str
    type_info: str  # e.g., "Integer", "Array", "Object"

@dataclass
class Block(ASTNode):
    statements: List['Statement'] = field(default_factory=list)

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Assignment(Statement):
    target: str
    value: 'Expression'

@dataclass
class IfStatement(Statement):
    condition: 'Expression'
    then_block: Block
    else_block: Optional[Block] = None

@dataclass
class ForLoop(Statement):
    variable: str
    start_value: 'Expression'
    end_value: 'Expression'
    body: Block

@dataclass
class WhileLoop(Statement):
    condition: 'Expression'
    body: Block

@dataclass
class RepeatLoop(Statement):
    condition: 'Expression'
    body: Block

@dataclass
class Call(Statement):
    procedure_name: str
    arguments: List['Expression']

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression

@dataclass
class Literal(Expression):
    value: Any
    type_name: str # "Integer", "Boolean", "String", "Null"

@dataclass
class Variable(Expression):
    name: str

@dataclass
class ArrayAccess(Expression):
    array_name: str
    index: Expression

@dataclass
class FieldAccess(Expression):
    object_name: str
    field_name: str
