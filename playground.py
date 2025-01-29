from phi.playground import Playground, serve_playground_app

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.file import FileTools

from phi.workflow import Workflow, RunResponse, RunEvent
import re
from phi.utils.log import logger

from typing import Optional, Iterator

from pydantic import BaseModel, Field

from prompts import MAIN_PROMPT_MBTI, MAIN_PROMPT_BIG5, MAIN_PROMPT_DISC, MAIN_PROMPT_Enneagram, MAIN_PROMPT_SocialStyles
from prompts import MAIN_PROMPT_Manager, MAIN_PROMPT_Simulation

from pathlib import Path
import os
import time

model = Groq(id="llama-3.3-70b-versatile")

work_dir = Path(__file__).parent.resolve()

file_name = input("Enter the name of the file: ")
MBTI_result_file_name = file_name[:-4]+"_MBTI.txt"
BIG5_result_file_name = file_name[:-4]+"_BIG5.txt"
DISC_result_file_name = file_name[:-4]+"_DISC.txt"
Enneagram_result_file_name = file_name[:-4]+"_Enneagram.txt"
SocialStyles_result_file_name = file_name[:-4]+"_SocialStyles.txt"
Profile_result_file_name = file_name[:-4]+"_Profile.txt"

name = input("Whose psychological profile are you interested in? ")
MAIN_PROMPT_Simulation = MAIN_PROMPT_Simulation.format(file_name=file_name, Profile_result_file_name=Profile_result_file_name, name=name)


Simulation_agent = Agent(
    name="Simulation",
    role="Psychologi Specialist",
    model=model,
    tools = [FileTools(base_dir=work_dir)],
    instructions=[MAIN_PROMPT_Simulation],
    show_tool_calls=False,
    markdown=True,
)

app = Playground(agents=[Simulation_agent]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
