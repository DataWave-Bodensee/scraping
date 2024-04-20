from openai import OpenAI
import json
from db_parameters import llm_tool, db_params


def _create_db_entry(args_from_llm, article, response_message_summary):
    """Creates a new entry in the database."""
    print(
        "Creating a new database entry...",
        args_from_llm,
        article.title,
        article.published,
        response_message_summary,
    )
    return "Database entry created successfully."


def llm_create_db_entry(article):
    """Takes an article as input and creates a new database entry, by utilizing a llm to extract the relevant information."""
    client = OpenAI()

    # Ask LLM, to call create_database_entry tool by extracting the relevant information from the given article.
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant, aimed at analysing text data and extracting relevant information.",
            },
            {
                "role": "user",
                "content": "Make a new database entry for the following article:",
            },
            {"role": "user", "content": article.content},
        ],
        temperature = 1.0,
        tools = llm_tool,
        tool_choice = "auto",
    ) 
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    response_summary = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant, aimed at analysing text data and extracting relevant information.",
            },
            {
                "role": "user",
                "content": "summarize the article in few sentences as possible:",
            },
            {"role": "user", "content": article.content},
        ],
        temperature=1.0,
    )

    response_message_summary = response_summary.choices[0].message.content

    if tool_calls:
        tool_call = tool_calls[
            0
        ]  # LLM can possibly make multiple functions calls, only take the first

        if tool_call.function.name != "create_database_entry":
            return "Error: Unexpected function call."
        function_args = json.loads(tool_call.function.arguments)

        # Check if all required arguments are present in the function call
        for arg in db_params:
            if arg not in function_args:
                return f"Error: No {arg} found in the function call. Function call: {function_args}"

        _create_db_entry(function_args, article, response_message_summary)

        return "Database entry created successfully."

    return "Error: No function call found."
