# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import os

import backoff as backoff
import openai
from dotenv import load_dotenv

from model import grammar, load_debate_from_file, load_from_file

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

system = \
f"""
The user will present a resolution. 
You must generate a debate of at least 20 parts of dialogue, adhering to the following Lark grammar. 
Premises should be high quality, and should not 

{grammar}
"""
candide_resolution = load_debate_from_file('examples/candide.txt').resolution.resolution
candide = "\n\n".join(load_from_file('examples/candide.txt').split("\n\n")[1:6])

global tokens

@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def debate(resolution: str):
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": candide_resolution},
            {"role": "assistant", "content": candide},
            {"role": "user", "content": resolution},
        ],
    )

    result = response['choices'][0].message.content
    tokens = response['usage']['total_tokens']

    return result


resolution = \
f"""An astronaut drops a 1.0 kg object and a 5.0 kg object on the Moon. 
Both objects fall a total distance of 2.0 m vertically. 
Which of the following best describes the objects after they have fallen a distance of 1.0 m? 
A) They have each gained one-half of their maximum kinetic energy. 
B) They have each lost kinetic energy."
"""
debate(resolution)