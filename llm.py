from openai import OpenAI
import json

def _create_db_entry(params):
    """Creates a new entry in the database."""
    print("Creating a new database entry...", params)
    return "Database entry created successfully."

def llm_create_db_entry(article):        
    """Takes an article as input and creates a new database entry, by utilizing a llm to extract the relevant information."""
    client = OpenAI()

    # Define a single tool, namely create_database_entry, which takes all the necessary parameters to create a new entry in the database.
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_database_entry",
                "description": "Create a new entry in the database with the given parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "An unique identifier for the entry.",
                        },
                        "treetype": {
                            "type": "string", 
                            "description": "The type of tree that was killed.",
                            "enum": ["Birke", "Buche"]
                        },
                        "year": {
                            "type": "integer",
                            "description": "The year the tree was killed.",
                        },
                        }
                    },
                "required": ["id", "treetype", "year"],
            },
        },
    ]
    db_required_args = ["id", "treetype", "year"]

    # Ask LLM, to call create_database_entry tool by extracting the relevant information from the given article.
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo-1106",
        messages = [
            {"role": "system", "content": "You are a helpful assistant, aimed at analysing text data and extracting relevant information."},
            {"role": "user", "content": "Make a new database entry for the following article:"},
            {"role": "user", "content": article},
        ],
        temperature = 1.0,
        tools = tools,
        tool_choice = "auto",
    ) 
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        tool_call = tool_calls[0] # LLM can possibly make multiple functions calls, only take the first
        
        if tool_call.function.name != "create_database_entry":
            return "Error: Unexpected function call."
        function_args = json.loads(tool_call.function.arguments)

        # Check if all required arguments are present in the function call
        for arg in db_required_args:
            if arg not in function_args:
                return f"Error: No {arg} found in the function call."        

        _create_db_entry(
            function_args
        )
        
        return "Database entry created successfully."
    
    return "Error: No function call found."


llm_create_db_entry("A birch tree was killed in 2022. ARTICLE_ID:23")