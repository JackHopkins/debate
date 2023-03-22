from typing import List, Optional, Union, Any
from pydantic import BaseModel
from lark import Lark, Transformer, v_args

grammar = '''
start: debate

debate: resolution introducing_speakers rules_of_engagement statements

resolution: "The resolution is" ESCAPED_STRING ";"
introducing_speakers: "The speakers are" speaker role ("," speaker role)* ";"

rules_of_engagement: "The rules of engagement are" rule ("," rule)* ";"
statements: statement (";" statement)* ";"

statement: speaker (argument | refutation | question | hypothesis | synthesis | meta_debate_construct)

role: "as" ESCAPED_STRING

argument: "argues that" proposition "by presenting" premises "and" evidence
premises: "the premise(s)" premise ("," premise)*
evidence: "the evidence" example ("," example)*

refutation: "refutes" proposition "by challenging" premises "and presenting" counter_evidence
counter_evidence: "counter-evidence" example ("," example)*

question: "asks" question_text
hypothesis: "presents the hypothesis" ESCAPED_STRING "to explain" proposition
synthesis: "synthesizes" proposition "and" proposition "to form the new hypothesis" proposition

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
'''

lark_parser = Lark(grammar, start='start', parser='lalr')


class Resolution(BaseModel):
    resolution: str


class Role(BaseModel):
    role: str


class Proposition(BaseModel):
    proposition: str


class Premise(BaseModel):
    premise: str


class Example(BaseModel):
    example: str


class QuestionText(BaseModel):
    question_text: str


class MetaDebateAction(BaseModel):
    meta_debate_action: str


class Speaker(BaseModel):
    speaker: str
    role: Optional[Role]


class Rule(BaseModel):
    rule: str


class Statement(BaseModel):
    speaker: Speaker
    content: Any


class RulesOfEngagement(BaseModel):
    rules: List[Rule]


class Statements(BaseModel):
    statements: List[Statement]


class Premises(BaseModel):
    premises: List[Premise]


class Evidence(BaseModel):
    evidence: List[Example]


class Argument(BaseModel):
    proposition: Proposition
    premises: Premises
    evidence: Evidence


class CounterEvidence(BaseModel):
    counter_evidence: List[Example]


class Refutation(BaseModel):
    proposition: Proposition
    premises: Premises
    counter_evidence: CounterEvidence


class Question(BaseModel):
    question_text: QuestionText


class Hypothesis(BaseModel):
    hypothesis: str
    proposition: Proposition


class Synthesis(BaseModel):
    proposition1: Proposition
    proposition2: Proposition
    proposition3: Proposition


class MetaDebateConstruct(BaseModel):
    meta_debate_action: MetaDebateAction


class Debate(BaseModel):
    resolution: Resolution
    introducing_speakers: Any
    rules_of_engagement: RulesOfEngagement
    statements: Statements

    def __str__(self):
        return self.resolution.resolution


class DebateTransformer(Transformer):
    @v_args(inline=True)
    def start(self, debate):
        return debate

    def debate(self, items):
        return Debate(resolution=items[0],
                      introducing_speakers=items[1],
                      rules_of_engagement=items[2],
                      statements=items[3])

    def resolution(self, items):
        return Resolution(resolution=items[0])

    def introduced_speaker(self, items):
        return Speaker(speaker=items[0].speaker, role=items[1])

    def rules_of_engagement(self, items):
        return RulesOfEngagement(rules=items)

    def statements(self, items):
        return Statements(statements=items)

    def statement(self, args):
        return Statement(speaker=args[0], content=args[1])

    def role(self, items):
        return Role(role=items[0])

    def argument(self, items):
        return Argument(proposition=items[0], premises=items[1], evidence=items[2])

    def premises(self, items):
        return Premises(premises=items)

    def evidence(self, items):
        return Evidence(evidence=items)

    def refutation(self, items):
        return Refutation(proposition=items[0], premises=items[1], counter_evidence=items[2])

    def counter_evidence(self, items):
        return CounterEvidence(counter_evidence=items)

    def question(self, items):
        return Question(question_text=items[0])

    def hypothesis(self, items):
        return Hypothesis(hypothesis=items[0], proposition=items[1])

    def synthesis(self, items):
        return Synthesis(proposition1=items[0], proposition2=items[1], proposition3=items[2])

    def meta_debate_construct(self, items):
        return MetaDebateConstruct(meta_debate_action=items[0])

    def proposition(self, items):
        return Proposition(proposition=items[0])

    def premise(self, items):
        return Premise(premise=items[0])

    def example(self, items):
        return Example(example=items[0])

    def question_text(self, items):
        return QuestionText(question_text=items[0])

    def meta_debate_action(self, items):
        return MetaDebateAction(meta_debate_action=items[0])

    def speaker(self, items):
        if len(items) > 1:
            return Speaker(speaker=items[0], role=items[1])
        return Speaker(speaker=items[0])

    def rule(self, items):
        return Rule(rule=items[0])


def parse(text: str) -> Debate:
    tree = lark_parser.parse(text)
    debate_transformer = DebateTransformer()
    return debate_transformer.transform(tree)


def load_from_file(file_path: str) -> Debate:
    with open(file_path, "r") as file:
        debate_text = file.read()
    return debate_text


def load_debate_from_file(file_path: str) -> Debate:
    return parse(load_from_file(file_path))


Statement.update_forward_refs()

if __name__ == "__main__":
    debate = load_debate_from_file("examples/candide.txt")
    print(debate)
