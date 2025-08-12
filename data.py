from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor 
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage 
from autogen_agentchat.base import TaskResult
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
api_key_name = "OPENAI_API_KEY"


async def main():
    model = OpenAIChatCompletionClient(model="gpt-4o", api_key=os.getenv(api_key_name))

    developer_agent = AssistantAgent(
        name="Developer",
        model_client=model,
        system_message="""You are a coding developer agent. You will
        be given a csv file and be asked a few questions about it. 
        You can develop python code to analyze the csv file and answer
        the questions. You should always write the code in a code bock
        with the language(python) specified.
        You should always begin with your plan to answer the question,
        then you should write the code to help answer the question.
        If you need several code blocks, make sure to write down one
        at a time. You will be working with a code execution agent.
        You must wait for the code execution agent to execute your code.
        If the code execution runs successfully, you can continue.
        Once you the the code execution results that you need to answer,
        you should provide a short summary with the final answer.
        After that, you should exactly say 'TERMINATE' to end the 
        conversation
        """,
    )

    docker_agent= DockerCommandLineCodeExecutor(
        work_dir="temp"
    )

    executor_agent = CodeExecutorAgent(
        name="CodeExecutor",
        code_executor=docker_agent,
    )

    team = RoundRobinGroupChat(
        participants=[developer_agent, executor_agent],
        name="Developer Team", 
        termination_condition=TextMentionTermination('TERMINATE'),
        max_turns=20,
    )

    await docker_agent.start()
    task = 'My dataset is "data.csv". What are the columns in this dataset?'
    async for msg in team.run_stream(task=task):
        if isinstance(msg, TextMessage):
            print(f"{msg.source}: {msg.content}")
        elif isinstance(msg, TaskResult):
            print(f"Stopping reason: {msg.stop_reason} ")
        
    await docker_agent.stop()
        

if __name__ == "__main__":
    asyncio.run(main())