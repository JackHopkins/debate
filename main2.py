from typing import List, Union
from pydantic import BaseModel
from lark import Lark, Transformer, v_args


class Rule(BaseModel):
    text: str


class Proposition(BaseModel):
    text: str


class Premise(BaseModel):
    text: str


class Example(BaseModel):
    text: str


class QuestionText(BaseModel):
    text: str


class MetaDebateAction(BaseModel):
    text: str


class Speaker(BaseModel):
    name: str


class Statement(BaseModel):
    speaker: Speaker
    content: Union['Argument', 'Refutation', 'Question', 'MetaDebateConstruct']


class Argument(BaseModel):
    proposition: Proposition
    premises: List[Premise]
    evidence: List[Example]


class Refutation(BaseModel):
    proposition: Proposition
    challenged_premises: List[Premise]
    counter_evidence: List[Example]


class Question(BaseModel):
    question_text: QuestionText


class MetaDebateConstruct(BaseModel):
    meta_debate_action: MetaDebateAction


class Resolution(BaseModel):
    proposition: Proposition


class RulesOfEngagement(BaseModel):
    rules: List[Rule]


class Debate(BaseModel):
    resolution: Resolution
    rules_of_engagement: RulesOfEngagement
    statements: List[Statement]


debate_grammar = r"""
    start: debate

    debate: resolution rules_of_engagement statements
    
    resolution: "The resolution is" ESCAPED_STRING ";"
    rules_of_engagement: "The rules of engagement are" rule ("," rule)* ";"
    statements: statement (";" statement)* ";"
    
    statement: speaker role? (argument | refutation | question | hypothesis | synthesis | meta_debate_construct)
    
    role: "as" ESCAPED_STRING
    
    argument: "argues that" proposition "by presenting" premises "and" evidence
    premises: "the premise(s)" premise ("," premise)*
    evidence: "the evidence" example ("," example)*
    
    refutation: "refutes" proposition "by challenging" premises "and presenting" counter_evidence
    counter_evidence: "counter-evidence" example ("," example)*
    
    question: "asks" question_text
    hypothesis: "presents the hypothesis" ESCAPED_STRING "to explain" proposition
    synthesis: "synthesizes" proposition "and" proposition "to form a new hypothesis" proposition
    
    meta_debate_construct: "comments on the debate process by" meta_debate_action
    
    proposition: ESCAPED_STRING
    premise: ESCAPED_STRING
    example: ESCAPED_STRING
    question_text: ESCAPED_STRING
    meta_debate_action: ESCAPED_STRING
    speaker: ESCAPED_STRING
    rule: ESCAPED_STRING
    
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS

"""


class DebateTransformer(Transformer):
    @v_args(inline=True)
    def debate(self, *args):
        resolution, rules_of_engagement, statements = args
        return Debate(resolution=resolution, rules_of_engagement=rules_of_engagement, statements=statements)

    resolution = lambda self, x: Resolution(proposition=Proposition(text=x[0]))
    rules_of_engagement = lambda self, x: RulesOfEngagement(rules=x)
    statements = lambda self, x: x

    statement = lambda self, x: Statement(speaker=x[0], content=x[1])

    argument = lambda self, x: Argument(proposition=x[0], premises=x[1], evidence=x[2])
    premises = lambda self, x: x
    evidence = lambda self, x: x

    refutation = lambda self, x: Refutation(proposition=x[0], challenged_premises=x[1], counter_evidence=x[2])
    counter_evidence = lambda self, x: x

    question = lambda self, x: Question(question_text=x[0])

    meta_debate_construct = lambda self, x: MetaDebateConstruct(meta_debate_action=x[0])

    proposition = lambda self, x: Proposition(text=x[0])
    premise = lambda self, x: Premise(text=x[0])
    example = lambda self, x: Example(text=x[0])
    question_text = lambda self, x: QuestionText(text=x[0])
    meta_debate_action = lambda self, x: MetaDebateAction(text=x[0])
    speaker = lambda self, x: Speaker(name=x[0])
    rule = lambda self, x: Rule(text=x[0])


lark_parser = Lark(debate_grammar, parser="lalr", start="start", transformer=DebateTransformer())


def load_debate_from_file(file_path: str) -> Debate:
    with open(file_path, "r") as file:
        debate_text = file.read()
    return lark_parser.parse(debate_text)

Statement.update_forward_refs()

if __name__ == "__main__":
    debate_file_path = "examples/physics.txt"
    debate = load_debate_from_file(debate_file_path)
    print(debate)
