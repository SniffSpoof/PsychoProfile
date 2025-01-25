from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.file import FileTools

from phi.workflow import Workflow, RunResponse, RunEvent
from phi.utils.pprint import pprint_run_response
from phi.utils.log import logger

from typing import Optional, Iterator

from pydantic import BaseModel, Field

from prompts import MAIN_PROMPT_MBTI, MAIN_PROMPT_BIG5, MAIN_PROMPT_DISC, MAIN_PROMPT_Enneagram, MAIN_PROMPT_Manager, MAIN_PROMPT_Simulation

from pathlib import Path

###############
# GLOBAL VARS #
###############
file_name = "FedorVera.txt"
MBTI_result_file_name = file_name[:-4]+"_MBTI.txt"
BIG5_result_file_name = file_name[:-4]+"_BIG5.txt"
DISC_result_file_name = file_name[:-4]+"_DISC.txt"
Enneagram_result_file_name = file_name[:-4]+"_Enneagram.txt"
Profile_result_file_name = file_name[:-4]+"_Profile.txt"

work_dir = Path("/home/sniffspoof/phidata")

model = Gemini(id="gemini-2.0-flash-exp")

PROMPT = """
    Follow the instructions described to you.
    Read the specified file, follow the instructions, and save the result to the specified file.
    The result must be saved only once and the work must be completed.
    """


class ProfileGenerator(Workflow):
    ################
    #    AGENTS    #
    ################
    MBTI: Agent = Agent(
        name="MBTI",
        role="MBTI Specialist",
        model=model,
        tools = [FileTools(base_dir=work_dir)],
        instructions=[MAIN_PROMPT_MBTI.format(file_name=file_name, MBTI_result_file_name=MBTI_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    BIG5: Agent = Agent(
        name="BIG5",
        role="BIG5 Specialist",
        model=model,
        tools = [FileTools(base_dir=work_dir)],
        instructions=[MAIN_PROMPT_BIG5.format(file_name=file_name, BIG5_result_file_name=BIG5_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    DISC: Agent = Agent(
        name="DISC",
        role="DISC Specialist",
        model=model,
        tools = [FileTools(base_dir=work_dir)],
        instructions=[MAIN_PROMPT_DISC.format(file_name=file_name, DISC_result_file_name=DISC_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    Enneagram: Agent = Agent(
        name="Enneagram",
        role="Enneagram Specialist",
        model=model,
        tools = [FileTools(base_dir=work_dir)],
        instructions=[MAIN_PROMPT_Enneagram.format(file_name=file_name, Enneagram_result_file_name=Enneagram_result_file_name)],
        show_tool_calls=False,
        markdown=True,
    )

    Manager: Agent = Agent(
        name="Manager",
        role="Summary Specialist",
        model=model,
        tools = [FileTools(base_dir=work_dir)],
        instructions=[MAIN_PROMPT_Manager.format(
                        file_name=file_name,
                        Enneagram_result_file_name=Enneagram_result_file_name,
                        DISC_result_file_name=DISC_result_file_name,
                        BIG5_result_file_name=BIG5_result_file_name,
                        MBTI_result_file_name=MBTI_result_file_name,
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

        if use_cache:
            cache_agent: Agent = Agent(
                name="Cache Agent",
                role="File Asistant",
                model=model,
                tools = [FileTools(base_dir=work_dir)],
                instructions=[MAIN_PROMPT_Manager.format(
                                file_name=file_name,
                                Enneagram_result_file_name=Enneagram_result_file_name,
                                DISC_result_file_name=DISC_result_file_name,
                                BIG5_result_file_name=BIG5_result_file_name,
                                MBTI_result_file_name=MBTI_result_file_name,
                                Profile_result_file_name=Profile_result_file_name
                                )],
                show_tool_calls=False,
                markdown=True,
            )

        #######################################################
        # Step 1: Generate files for each psychological model #
        #######################################################
        logger.info("Generate files for each psychological model")
        try:
            #self.MBTI.print_response(PROMPT, stream=True)
            #self.BIG5.print_response(PROMPT, stream=True)
            #self.DISC.print_response(PROMPT, stream=True)
            #self.Enneagram.print_response(PROMPT, stream=True)

            logger.info("Starting MBTI_Agent")
            MBTI_response: RunResponse = self.MBTI.run(PROMPT)
            logger.info("MBTI_Agent finished")

            logger.info("Starting BIG5_Agent")
            BIG5_response: RunResponse = self.BIG5.run(PROMPT)
            logger.info("BIG5_Agent finished")

            logger.info("Starting DISC_Agent")
            DISC_response: RunResponse = self.DISC.run(PROMPT)
            logger.info("DISC_Agent finished")

            logger.info("Starting Enneagram_Agent")
            Enneagram_response: RunResponse = self.Enneagram.run(PROMPT)
            logger.info("Enneagram_Agent finished")
        except Exception as e:
            logger.warning(f"Error running agents: {e}")

        #######################################################
        # Step 1.1: Check If some files have not been created #
        #######################################################
        files_to_check = {
            MBTI_result_file_name: self.MBTI.run,
            BIG5_result_file_name: self.BIG5.run,
            DISC_result_file_name: self.DISC.run,
            Enneagram_result_file_name: self.Enneagram.run,
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
                max_retries = 3
                retries = 1
                while not file_path.exists() and retries <= max_retries:
                    logger.info(f"{missing_file} missed. Rerunning the agent")
                    response: RunResponse = agent_run_method(PROMPT+"Please dont forget to save file!")
                    logger.info(f"{missing_file.split('_')[0]}_Agent finished")
                    retries += 1


        #####################################################
        #Step 2: Generating the final psychological profile #
        #####################################################
        logger.info("Generating the final psychological profile")
        try:
            #self.Manager.print_response(PROMPT, stream=True)
            logger.info("Starting profile generator agent")
            Manager_response: RunResponse = self.Manager.run(PROMPT)
            logger.info("Profile generator agent finished")
        except Exception as e:
            logger.warning(f"Error running agent: {e}")

        #################################################
        # Step 2.1: Check If file have not been created #
        #################################################
        file_path = work_dir / Profile_result_file_name
        if not file_path.exists():
            logger.warning("Profile file have not been created")
            max_retries = 3
            retries = 1
            while not file_path.exists() and retries <= 3:
                logger.info("Profile file missed. Rerunning the agent")
                Enneagram_response: RunResponse = self.Enneagram.run(PROMPT+"Please dont forget to save file!")
                logger.info("Profile generator agent finished")
                retries+=1


if __name__ == "__main__":
    generate_profile = ProfileGenerator(
        session_id=f"generate-profile-on-{file_name}"
        )

    profile: Iterator[RunResponse] = generate_profile.run(file_name=file_name)
    logger.info("Psychological profiles generated")
    if input("Do you want continue (Y/N)? ").lower() == "y":
        name = input("Whose psychological profile are you interested in? ")

        #init agent
        Simulation_agent = Agent(
            name="Simulation",
            role="Psychologi Specialist",
            model=model,
            tools = [FileTools(base_dir=work_dir)],
            instructions=[MAIN_PROMPT_Simulation.format(Profile_result_file_name=Profile_result_file_name, name=name)],
            show_tool_calls=False,
            markdown=True,
        )
        prompt = ""
        while prompt.lower() != "stop":
            prompt = input("Enter the phrase you'd like to simulate with (or 'stop' to exit): ")
            Simulation_agent.print_response(prompt, stream=True)
