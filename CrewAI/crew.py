from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import FileReadTool
read_file_tool = FileReadTool(file_path='enter your file path')
read_file_tool_profile = FileReadTool(file_path='enter your file path')

from crewai_tools import FileWriterTool
file_writer_tool = FileWriterTool()


@CrewBase
class Psycho():
	"""Psycho crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def MBTI_Agent(self) -> Agent:
		return Agent(
			config=self.agents_config['MBTI_Agent'],
			tools=[read_file_tool, file_writer_tool],
			verbose=True
		)

	@agent
	def BigFive_Agent(self) -> Agent:
		return Agent(
			config=self.agents_config['BigFive_Agent'],
			tools=[read_file_tool, file_writer_tool],
			verbose=True
		)

	@agent
	def DISC_Agent(self) -> Agent:
		return Agent(
			config=self.agents_config['DISC_Agent'],
			tools=[read_file_tool, file_writer_tool],
			verbose=True
		)

	@agent
	def Enneagram_Agent(self) -> Agent:
		return Agent(
			config=self.agents_config['Enneagram_Agent'],
			tools=[read_file_tool, file_writer_tool],
			verbose=True
		)

	@agent
	def Psychologist_Agent(self) -> Agent:
		return Agent(
			config=self.agents_config['Psychologist_Agent'],
			tools=[read_file_tool, file_writer_tool],
			verbose=True
		)

	@agent
	def Simulation_Agent(self) -> Agent:
		return Agent(
			config=self.agents_config['Simulation_Agent'],
			tools=[read_file_tool_profile],
			verbose=True
		)

	@task
	def MBTI_task(self) -> Task:
		return Task(
			config=self.tasks_config['MBTI_task'],
		)

	@task
	def BigFive_task(self) -> Task:
		return Task(
			config=self.tasks_config['BigFive_task'],
		)

	@task
	def DISC_task(self) -> Task:
		return Task(
			config=self.tasks_config['DISC_task'],
		)

	@task
	def Enneagram_task(self) -> Task:
		return Task(
			config=self.tasks_config['Enneagram_task'],
		)

	@task
	def Psychologist_task(self) -> Task:
		return Task(
			config=self.tasks_config['Psychologist_task'],
		)

	@task
	def Simulation_task(self) -> Task:
		return Task(
			config=self.tasks_config['Simulation_task']
		)

	def crew(self):
		crew_MBTI = Crew(agents=[self.MBTI_Agent()], tasks=[self.MBTI_task()])
		crew_BigFive = Crew(agents=[self.BigFive_Agent()], tasks=[self.BigFive_task()])
		crew_DISC = Crew(agents=[self.DISC_Agent()], tasks=[self.DISC_task()])
		crew_Enneagram = Crew(agents=[self.Enneagram_Agent()], tasks=[self.Enneagram_task()])

		return crew_MBTI, crew_BigFive, crew_DISC, crew_Enneagram

	def psychologist(self):
		return Crew(agents=[self.Psychologist_Agent()], tasks=[self.Psychologist_task()])

	def simulatation(self):
		return Crew(agents=[self.Simulation_Agent()], tasks=[self.Simulation_task()])
