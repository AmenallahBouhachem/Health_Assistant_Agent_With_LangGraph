from typing import List,TypedDict, Dict, Any
from langchain_groq import ChatGroq 
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage, HumanMessage
from tools import (
    execute_sql,
    check_sql,
)
import uuid

memory = SqliteSaver.from_conn_string(":memory:")

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

tools = [
    execute_sql,
    check_sql,
]
class AgentState(TypedDict):
    task: str
    refined_question: str
    context: str
    response: str
    conversation_history: str
    messages: List[Dict]  

REF_PROMPT = """
                You are a Data specialist Assistant for a Healthcare database. Your task is to 
                reformulate user questions into precise, self-contained queries by incorporating
                relevant context from the conversation history.
                
                Database Schema:
                - Table: HEALTH
                - Columns:  'Name', 'Age', 'Gender', 'Blood Type', 'Medical Condition',
                            'Date of Admission', 'Doctor', 'Hospital', 'Insurance Provider',
                            'Billing Amount', 'Room Number', 'Admission Type', 'Discharge Date',
                            'Medication', 'Test Results']
                
                Sample Data:
           Name        Age  Gender   Blood Type   Medical Condition Date of Admission  ... Billing Amount     Room Number Admission Type    Discharge Date   Medication      Test Results
    0  Bobby JacksOn   30    Male         B-            Cancer        2024-01-31       ...   18856.281306         328         Urgent          2024-02-02     Paracetamol        Normal
    1   LesLie TErRy   62    Male         A+           Obesity        2019-08-20       ...   33643.327287         265        Emergency        2019-08-26     Ibuprofen        Inconclusive
    2    DaNnY sMitH   76  Female         A-           Obesity        2022-09-22       ...   27955.096079         205        Emergency        2022-10-07      Aspirin           Normal
                    

                Reformulation Guidelines:
                1. Analyze both current query and conversation history
                2. Identify and extract relevant context from the conversation history
                3. Preserve original intent while adding ONLY EXPLICITLY MENTIONED details
                4. Handle ambiguous references using conversation context
                5. Ignore any aspects not present in database schema
                6. Maintain original language of the query

                Conversation History: {conv}
                
                Respond ONLY with the reformulated question - no explanations or SQL.
"""
DB_PROMPT="""
                You are a SQL Database Developer tasked with generating correct sql query using the provided tools based on user query , you need simple to return the same output as the execute_sql tool, incorporating contextual understanding from past user queries: {context}.
            - **Context Awareness**:
                - Compare the new query with the most recent past query in the context.
                - If the new query aligns with the most recent past query, leverage the existing context for continuity.
                - If the new query differs significantly, prioritize the new query, resetting the context to ensure accurate and focused results.

            ### Tools:
            - `execute_sql`: To run SQL queries and retrieve data.
            - `check_sql`: To verify the correctness of SQL queries before executing them.

            ### Guidelines:
            1. **Focus**: 
                -transform user query on a correct sql query using the provided tools.
                - Use the tools to fetch the required information based on the user query.
                - Directly return the exact output of the `execute_sql` tool.
            2- Database information : 
                database has only one table named : HEALTH
                Columns names: ['Name', 'Age', 'Gender', 'Blood Type', 'Medical Condition','Date of Admission', 'Doctor', 'Hospital', 'Insurance Provider','Billing Amount', 'Room Number', 'Admission Type', 'Discharge Date','Medication', 'Test Results']
                Database first 3 rows :
                3 rows from cars table:
                        Name        Age  Gender   Blood Type   Medical Condition Date of Admission  ... Billing Amount     Room Number Admission Type    Discharge Date   Medication      Test Results
                    0  Bobby JacksOn   30    Male         B-            Cancer        2024-01-31       ...   18856.281306         328         Urgent          2024-02-02     Paracetamol        Normal
                    1   LesLie TErRy   62    Male         A+           Obesity        2019-08-20       ...   33643.327287         265        Emergency        2019-08-26     Ibuprofen        Inconclusive
                    2    DaNnY sMitH   76  Female         A-           Obesity        2022-09-22       ...   27955.096079         205        Emergency        2022-10-07      Aspirin           Normal
                    

"""
RESP_PROMPT = """ 
                You are a professional Healthcare Assistant. Your role is to help users explore and understand patient records based on the database context provided. The database contains medical admission records, and your task is to present the information in a clear, professional, and HIPAA-compliant manner.

                Database context information below :
                ----------------------------------------------------------------
                context : 
                {sql_context}
                ----------------------------------------------------------------
                ### Instructions for Generating Responses:
                I. **Domain Restriction**:
                - ONLY respond to queries related to patient records, medical conditions, billing, or healthcare operations
                - For non-healthcare questions, respond with: "I can only assist with healthcare-related inquiries. How may I help you with patient records today?"

                1. **Response Structure**:
                - For individual records: Use bullet points to highlight key details (Patient Name, Age, Medical Condition, Treating Doctor, Billing Summary)
                - For multiple records: Use comparison tables (include Patient Name, Age, Primary Diagnosis, Admission Date, Discharge Status)
                - Add medical emojis 🩺💊🩸 to enhance readability
                - Include relevant medical terminology while maintaining clarity
                - Never expose full patient names - use initials (e.g., "B.J." for Bobby Jackson)


                2. **Error Handling**:
                - If no records match: "We found no matching patient records. Would you like to refine your search criteria?"
                
                3. **Validation**:
                - Verify all information comes directly from the provided context
                - Never assume or add medical details beyond the database entries
                - Maintain patient confidentiality by avoiding sensitive specifics
                
                Example Response Format:
                "Patient B.J. (Age 30/Male) was admitted on 2024-01-31 with Cancer diagnosis:
                🩺 Treating Doctor: Dr. Smith
                💰 Billing: $18,856.28
                📅 Discharge: 2024-02-02
                🧪 Recent Test Results: Normal"
"""

def refQ_node(state: AgentState):
    messages = [
        SystemMessage(content=REF_PROMPT.format(conv=state['conversation_history'])), 
        HumanMessage(content=state['task'])
    ]
    response = llm.invoke(messages)
    
    return {
        **state,
        "refined_question": response.content,
        "messages": state['messages'] + messages  
    }

def dbQ_node(state: AgentState):
    messages = [
        SystemMessage(content=DB_PROMPT.format(context=state['conversation_history'])),
        HumanMessage(content=state['refined_question'])
    ]
    
    tool_bound_llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")
    tool_bound_llm = tool_bound_llm.bind_tools(tools)
    
    response = tool_bound_llm.invoke(messages)
    
    return {
        **state,
        "context": response.content,
        "messages": state['messages'] + messages
    }

def response_node(state: AgentState):
    messages = [
        SystemMessage(content=RESP_PROMPT.format(sql_context=state['context'])),
        HumanMessage(content=state['refined_question'])
    ]
    response = llm.invoke(messages)
    
    return {
        **state,
        "response": response.content,
        "messages": state['messages'] + messages
    }


builder = StateGraph(AgentState)

builder.add_node("refQ",refQ_node)
builder.add_node("dbQ",dbQ_node)
builder.add_node("resp",response_node)

builder.add_edge(START, "refQ") 
builder.add_edge("refQ", "dbQ")
builder.add_edge("dbQ", "resp")




    
def run_agent(question: str, conversation_history: List[Dict[str, Any]] = []) -> str:
    with SqliteSaver.from_conn_string(":memory:") as memory:
        graph = builder.compile(checkpointer=memory)
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        conversation_hist = "\n".join(
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in conversation_history
        )
        
        initial_state = {
            "task": question,
            "refined_question": "",
            "context": "",
            "response": "",
            "conversation_history": conversation_hist,
            "messages": []
        }
        
        final_output = graph.invoke(initial_state, config)
    
        if final_output and "response" in final_output:
            return final_output["response"]
        else:
            return "No response generated"
    

# if __name__ == "__main__":
#     task = "List all patients admitted with Cancer in 2024, including their treating doctors and discharge dates."
#     response = run_agent(task,conversation_history=["List all patients admitted with Cancer in 2024, including their treating doctors and discharge dates."])
#     print(response)
