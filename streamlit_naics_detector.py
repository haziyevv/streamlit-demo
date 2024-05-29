import streamlit as st
# from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.agents import (
AgentExecutor, AgentType, initialize_agent, load_tools
)
import re
from openai import OpenAI


import pandas as pd
import pdb, json

import pickle
from dotenv import load_dotenv
import os

load_dotenv()

# Retrieve the API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")


gpt_assistant_prompt = "You are a helpful assistant designed to output JSON and your purpose is to decide the industry of the given company name."

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
)

# create a langchain prompt
gpt_user_prompt = """I will give you the name of the company and you will decide the NAICS code id it belongs to, with its description.
Please return the result in the following format, do not include any explanations:
{{
"NAICS code": "NAICS code",
"description": "description of NAICS code"
}}
Utilize your expertise to generate the most pertinent information.
Company Name: "Sony"
Response: {{"NAICS code": "334610", "description": "Manufacturing and Reproducing Magnetic and Optical Media"}}
Company Name: {}
"""

import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from duckduckgo_search import DDGS

st_callback = StreamlitCallbackHandler(st.container())

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            results = DDGS().text(prompt, max_results=10)
            titles = [re.findall("\w+", x["title"].lower()) for x in results]
            re_name = re.findall("\w+", prompt.lower())
            similars = [len(set(x).intersection(re_name)) for x in titles]
            sorted_indices = sorted(range(len(similars)), key=lambda i: similars[i], reverse=True)[:3]

            context = ""
            for x in sorted_indices:
                context += results[x]["body"] + " "
            st.write("Search completed!")

        # Display the search results
        st.write("Top search results:")
        for x in sorted_indices:
            st.write(f"Title: {results[x]['title']}")
            st.write(f"Body: {results[x]['body'][:200]}...")  # Displaying a snippet of the body


        message=[{"role": "assistant", "content": gpt_assistant_prompt}, {"role": "user", "content": gpt_user_prompt.format(prompt) + " context: " + context}]

        st.write("Assistant is thinking...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages = message,
            temperature=0.0001,
            max_tokens=300,
            frequency_penalty=0.0
        )   
        st.write("Response received!")

        response = json.loads(response.choices[0].message.content)
        st.write(response)
