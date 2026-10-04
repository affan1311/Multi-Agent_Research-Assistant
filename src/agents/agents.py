from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import search_web,scrape_url
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, max_output_tokens=1024)  

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[search_web]
        )

def build_scrape_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
        )

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that writes content based on the provided information."),
    ("human", """Write a detailed article based on the following information.
Topic: {topic}

Research Notes: {research}

Structure the report as:
-introduction
-key findings
-conclusion
-Sources

be detailed, factual and professional in your writing. Use the research notes to support your points and provide a comprehensive overview of the topic.""")
])

writer_chain = writer_prompt | llm | StrOutputParser()

# Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that critiques content based on the provided information."),
    ("human", """Critique the following article based on the research notes provided.
Report: {report}

Respond in this exact format:
Score: [0-10]
Stengths: 
- ....
- ....

Areas for Improvement:
- ....
- ....

One line verdict:
- ....
    """)
])
critic_chain = critic_prompt | llm | StrOutputParser()
