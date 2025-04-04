from dotenv import load_dotenv
import os
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from langchain.agents import tool
from langchain_groq import ChatGroq

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")


db = SQLDatabase.from_uri("sqlite:///healthcare.db")


@tool("execute_sql")
def execute_sql(sql_query: str) -> str:
    """Execute a SQL query against the database. Returns the result"""
    db = SQLDatabase.from_uri("sqlite:///healthcare.db")

    result = QuerySQLDataBaseTool(db=db, return_direct=True).invoke(sql_query)

    return result

@tool("check_sql")
def check_sql(sql_query: str) -> str:
    """
    Use this tool to double check if your query is correct before executing it.
    Always use this tool before executing a query with `execute_sql`.

    """
    db = SQLDatabase.from_uri("sqlite:///healthcare.db")

    
    return QuerySQLCheckerTool(db=db, llm=llm).invoke({"query": sql_query})


