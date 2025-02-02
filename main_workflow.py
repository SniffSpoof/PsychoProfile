from phi.agent import Agent
from phi.model.google import Gemini
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

###############
# GLOBAL VARS #
###############
file_name = input("Enter the name of the file: ")
MBTI_result_file_name = file_name[:-4]+"_MBTI.txt"
BIG5_result_file_name = file_name[:-4]+"_BIG5.txt"
DISC_result_file_name = file_name[:-4]+"_DISC.txt"
Enneagram_result_file_name = file_name[:-4]+"_Enneagram.txt"
SocialStyles_result_file_name = file_name[:-4]+"_SocialStyles.txt"
Profile_result_file_name = file_name[:-4]+"_Profile.txt"

work_dir = Path(__file__).parent.resolve()

model = Groq(id="deepseek-r1-distill-llama-70b", api_key="")

is_Groq = isinstance(model, Groq)

tools = None if is_Groq else [FileTools(base_dir=work_dir)]

PROMPT = """
    Follow the instructions described to you.
    Read the specified file, follow the instructions, and save the result to the specified file.
    The result must be saved only once and the work must be completed.
    """

PROMPT = open(file_name, "r").read() if is_Groq else PROMPT

class ProfileGenerator(Workflow):
    ################
    #    AGENTS    #
    ################
    MBTI: Agent = Agent(
        name="MBTI",
        role="MBTI Specialist",
        model=model,
        tools = tools,
        instructions=[MAIN_PROMPT_MBTI.format(file_name=file_name, MBTI_result_file_name=MBTI_result_file_name)],
        show_tool_calls=False,
        markdown=True
    )

    BIG5: Agent = Agent(
        name="BIG5",
        role="BIG5 Specialist",
        model=model,
        tools = tools,
        instructions=[MAIN_PROMPT_BIG5.format(file_name=file_name, BIG5_result_file_name=BIG5_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    DISC: Agent = Agent(
        name="DISC",
        role="DISC Specialist",
        model=model,
        tools = tools,
        instructions=[MAIN_PROMPT_DISC.format(file_name=file_name, DISC_result_file_name=DISC_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    Enneagram: Agent = Agent(
        name="Enneagram",
        role="Enneagram Specialist",
        model=model,
        tools = tools,
        instructions=[MAIN_PROMPT_Enneagram.format(file_name=file_name, Enneagram_result_file_name=Enneagram_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    SocialStyles: Agent = Agent(
        name="Social Styles",
        role="Social Styles Specialist",
        model=model,
        tools = tools,
        instructions=[MAIN_PROMPT_SocialStyles.format(file_name=file_name, SocialStyles_result_file_name=SocialStyles_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    Manager: Agent = Agent(
        name="Manager",
        role="Summary Specialist",
        model=model,
        tools = tools,
        instructions=[MAIN_PROMPT_Manager.format(
                        file_name=file_name,
                        Enneagram_result_file_name=Enneagram_result_file_name,
                        DISC_result_file_name=DISC_result_file_name,
                        BIG5_result_file_name=BIG5_result_file_name,
                        MBTI_result_file_name=MBTI_result_file_name,
                        SocialStyles_result_file_name=SocialStyles_result_file_name,
                        Profile_result_file_name=Profile_result_file_name
                        )],
        show_tool_calls=False,
        markdown=True,
    )

    ##################
    # WORKFLOW LOGIC #
    ##################
    def run (self,
             file_name: str,
             use_cache: bool = False
             ) -> Iterator[RunResponse]:

        logger.info(f"Starting workflow with id:{self.session_id}")

        def is_file_valid(file_path: Path):
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    #todo Cache Agent
                    return len(content) > 50
            return False

        def time_logger(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds.")
                return result
            return wrapper

        @time_logger
        def MBTI_run(p: str):
            if is_Groq:
                with open(MBTI_result_file_name, "w") as file:
                    file.write(self.MBTI.run(p).content)
            else:
                return self.MBTI.run(p)

        @time_logger
        def BIG5_run(p: str):
            if is_Groq:
                with open(BIG5_result_file_name, "w") as file:
                    file.write(self.BIG5.run(p).content)
            else:
                return self.BIG5.run(p)

        @time_logger
        def DISC_run(p: str):
            if is_Groq:
                with open(DISC_result_file_name, "w") as file:
                    file.write(self.DISC.run(p).content)
            else:
                return self.DISC.run(p)

        @time_logger
        def Enneagram_run(p: str):
            if is_Groq:
                with open(Enneagram_result_file_name, "w") as file:
                    file.write(self.Enneagram.run(p).content)
            else:
                return self.Enneagram.run(p)

        @time_logger
        def SocialStyles_run(p: str):
            if is_Groq:
                with open(SocialStyles_result_file_name, "w") as file:
                    file.write(self.SocialStyles.run(p).content)
            else:
                return self.SocialStyles.run(p)

        @time_logger
        def Manager_run(p: str):
            if is_Groq:
                prompt = ""
                with open(MBTI_result_file_name, "r") as file:
                    prompt += file.read()
                with open(BIG5_result_file_name, "r") as file:
                    prompt += file.read()
                with open(DISC_result_file_name, "r") as file:
                    prompt += file.read()
                with open(Enneagram_result_file_name, "r") as file:
                    prompt += file.read()
                with open(SocialStyles_result_file_name, "r") as file:
                    prompt += file.read()

                with open(Profile_result_file_name, "w") as file:
                    temp = self.Manager.run(p)
                    file.write(temp.content)
                    return temp
            else:
                return self.Manager.run(p)


        ########################################################################
        # Step 0: Checking already prepared files for each psychological model #
        ########################################################################
        if use_cache:
            logger.info("Checking cache...")
            files_to_check = {
                MBTI_result_file_name: MBTI_run,
                BIG5_result_file_name: BIG5_run,
                DISC_result_file_name: DISC_run,
                Enneagram_result_file_name: Enneagram_run,
                SocialStyles_result_file_name: SocialStyles_run
            }

            missing_files = []
            for result_file, agent_run_method in files_to_check.items():
                file_path = work_dir / result_file
                if not is_file_valid(file_path):
                    missing_files.append((result_file, agent_run_method))

            if not missing_files:
                logger.info("All files are cached and valid. Skipping agent execution.")

            logger.warning("Missing or invalid files detected:")
            for missing_file, _ in missing_files:
                logger.warning(f"- {missing_file}")
            logger.info("Rerunning agents for missing files")

            for missing_file, agent_run_method in missing_files:
                file_path = work_dir / missing_file
                max_retries = 5
                retries = 1
                while not file_path.exists() or not is_file_valid(file_path):
                    if retries > max_retries:
                        logger.error(f"Failed to generate {missing_file} after {max_retries} retries")
                        break
                    logger.info(f"Generating missing file: {missing_file} (Attempt {retries})")
                    agent_run_method(PROMPT)
                    retries += 1

        #######################################################
        # Step 1: Generate files for each psychological model #
        #######################################################
        else:
            logger.info("Generate files for each psychological model")
            try:
                logger.info("Starting MBTI_Agent")
                MBTI_response: RunResponse = MBTI_run(PROMPT)
                logger.info("MBTI_Agent finished")

                logger.info("Starting BIG5_Agent")
                BIG5_response: RunResponse = BIG5_run(PROMPT)
                logger.info("BIG5_Agent finished")

                logger.info("Starting DISC_Agent")
                DISC_response: RunResponse = DISC_run(PROMPT)
                logger.info("DISC_Agent finished")

                logger.info("Starting Enneagram_Agent")
                Enneagram_response: RunResponse = Enneagram_run(PROMPT)
                logger.info("Enneagram_Agent finished")

                logger.info("Starting SocialStyles_Agent")
                Enneagram_response: RunResponse = SocialStyles_run(PROMPT)
                logger.info("SocialStyles_Agent finished")
            except Exception as e:
                logger.warning(f"Error running agents: {e}")

            #######################################################
            # Step 1.1: Check If some files have not been created #
            #######################################################
            files_to_check = {
                MBTI_result_file_name: MBTI_run,
                BIG5_result_file_name: BIG5_run,
                DISC_result_file_name: DISC_run,
                Enneagram_result_file_name: Enneagram_run,
                SocialStyles_result_file_name: SocialStyles_run
            }

            missing_files = []
            for file_name, agent_run_method in files_to_check.items():
                file_path = work_dir / file_name
                if not file_path.exists():
                    missing_files.append((file_name, agent_run_method))

            if missing_files:
                logger.warning("Missing files:")
                for missing_file, _ in missing_files:
                    logger.warning(f"- {missing_file}")
                logger.info("Rerunning agents with missing files")
                for missing_file, agent_run_method in missing_files:
                    file_path = work_dir / missing_file
                    max_retries = 5
                    retries = 1
                    while not file_path.exists() and retries <= max_retries:
                        logger.info(f"{missing_file} missed. Rerunning the agent")
                        response: RunResponse = agent_run_method(PROMPT)
                        logger.info(f"{missing_file.split('_')[0]}_Agent finished")
                        retries += 1


        #####################################################
        #Step 2: Generating the final psychological profile #
        #####################################################
        logger.info("Generating the final psychological profile")
        try:
            #self.Manager.print_response(PROMPT, stream=True)
            logger.info("Starting profile generator agent")
            Manager_response: RunResponse = Manager_run(PROMPT)
            logger.info("Profile generator agent finished")
            return Manager_response
        except Exception as e:
            logger.warning(f"Error running agent: {e}")

        #################################################
        # Step 2.1: Check If file have not been created #
        #################################################
        file_path = work_dir / Profile_result_file_name
        if not file_path.exists():
            logger.warning("Profile file have not been created")
            max_retries = 15
            retries = 1
            while not file_path.exists() and retries <= max_retries:
                logger.info("Profile file missed. Rerunning the agent")
                Manager_response: RunResponse = Manager_run(PROMPT)
                logger.info("Profile generator agent finished")
                retries+=1

            return Manager_response


if __name__ == "__main__":
    generate_profile = ProfileGenerator(
        session_id=f"generate-profile-on-{file_name}"
        )

    profile: Iterator[RunResponse] = generate_profile.run(file_name=file_name, use_cache=True)
    logger.info("Psychological profiles generated")
    
    if input("Do you want continue (Y/N)? ").lower() == "y":
        name = input("Whose psychological profile are you interested in? ")

        MAIN_PROMPT_Simulation = MAIN_PROMPT_Simulation.format(file_name=file_name, Profile_result_file_name=Profile_result_file_name, name=name)

        if is_Groq:
            profile_text = ""
            context_text = ""

            with open(Profile_result_file_name) as file:
                profile_text += file.read()

            with open(file_name) as file:
                context_text += file.read()

            MAIN_PROMPT_Simulation += "\nProfile:\n" + profile_text + "\nContext:\n" + context_text

        Simulation_agent = Agent(
            name="Simulation",
            role="Psychologi Specialist",
            model=model,
            tools = tools,
            instructions=[MAIN_PROMPT_Simulation],
            show_tool_calls=False,
            markdown=True,
        )

        prompt = ""
        while prompt.lower() != "stop":
            prompt = input("Enter the phrase you'd like to simulate with (or 'stop' to exit): ")
            Simulation_agent.print_response(prompt, stream=True)
