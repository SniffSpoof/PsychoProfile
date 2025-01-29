#!/usr/bin/env python
import sys
import warnings

import asyncio
from time import sleep

from psycho.crew import Psycho

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """

    inputs = {
        'file_name': input("Enter the name of the file: "),
        'file_path': input("Enter the file path: ")
    }

    if "y" in input("Create files (y/n)? ").lower():
        crew_MBTI, crew_BigFive, crew_DISC, crew_Enneagram = Psycho().crew()

        async def async_crews():

        	result_MBTI = crew_MBTI.kickoff_async(inputs=inputs)
        	result_BigFive = crew_BigFive.kickoff_async(inputs=inputs)
        	result_DISC = crew_DISC.kickoff_async(inputs=inputs)
        	result_Enneagram = crew_Enneagram.kickoff_async(inputs=inputs)

        	results = await asyncio.gather(result_MBTI, result_BigFive, result_DISC, result_Enneagram)

        asyncio.run(async_crews())

        sleep(10)

        psychologist_crew = Psycho().psychologist()
        psychologist_crew.kickoff(inputs=inputs)

    else:
        inputs += {
            'name': input("Whose psychological profile are you interested in? "),
            'text': input("Enter the phrase you'd like to simulate with (or 'stop' to exit): "),
        }

        simulatation_crew = Psycho().simulatation()
        simulatation_crew.kickoff(inputs=inputs)
