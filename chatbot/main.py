import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config import settings

# Import your FastAPI-compatible tools
from fastapi_tools import _create_task, _delete_task, _update_task, _list_tasks



# Set OpenAI API Key from settings
os.environ["OPENAI_API_KEY"] = settings.openai_api_key

# Initialize the LLM
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("LLM:", llm)

# Define the agent prompt
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful AI assistant. Your goal is to help the user manage their ToDo tasks."),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessage(content="{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_chatbot():
    print("Hello! I am your ToDo assistant. How can I help you today?")
    chat_history = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = agent_executor.invoke({"input": user_input, "chat_history": chat_history})
        print(f'AI: {response["output"]}')
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response["output"]))

if __name__ == "__main__":
    run_chatbot()
