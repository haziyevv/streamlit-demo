import os
import re
import json
import requests
import pickle

import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler

from search_api import SearchSerper
from config import OPENAI_API_URL, OPENAI_API_KEY
from prompts import gpt_assistant_prompt, gpt_user_prompt

with open("naics_17to22.pkl", "rb") as fr:
    naics_17to22 = pickle.load(fr)

with open("naics_22.pkl", "rb") as fr:
    naics_desc = pickle.load(fr)

load_dotenv()

search_api = SearchSerper()

st_callback = StreamlitCallbackHandler(st.container())

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                results = search_api.search(prompt)
                context = " ".join(x["body"] for x in results)
                st.write("Search completed!")
            except Exception as e:
                st.error(f"Error: {e}")
                context = ""
                results = []
        if context:
            st.write("Top search results:")
            for result in results:
                st.write(f"Title: {result['title']}")
                st.write(f"Body: {result['body'][:200]}...")  # Displaying a snippet of the body
        else:
            st.write("No search results found. Will use knowledge of the LLM.")
        message=[{"role": "assistant", "content": gpt_assistant_prompt}, {"role": "user", "content": gpt_user_prompt.format(prompt) + " context: " + context}]

        st.write("Assistant is thinking...")

        requst_data = {
            'model': 'gpt-4o',
            'messages': message,
            'temperature': 0.001,
            'max_tokens': 300,
            'frequency_penalty': 0.0,
            'n': 3,
            'response_format': {"type": "json_object"},
        }

        response = requests.post(
            OPENAI_API_URL,
            headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
            json=requst_data
        )

        st.write("Response received!")
        if response.status_code == 401:
            st.error("Invalid OpenAI API key")
        else:
            result = response.json()
            results = [json.loads(x['message']['content']) for x in result['choices']]
            codes = set([x["NAICS_code"] for x in results])
            seen = set()
            results_filtered = []

            for result in results:
                naics_code = result["NAICS_code"]

                if naics_code in naics_17to22:
                    print(naics_code)
                    naics_code = naics_17to22[naics_code]
                if naics_code in seen:
                    continue
                description = naics_desc.get(naics_code, result["description"])
                result = {"NAICS_code": naics_code, "description": description}
                results_filtered.append(result)
                seen.add(naics_code)
            st.write(results_filtered)
