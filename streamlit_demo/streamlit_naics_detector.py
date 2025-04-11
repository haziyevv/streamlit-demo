import os
import json
import requests
import pickle
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler

from search_api import SearchSerper
from config import OPENAI_API_URL, OPENAI_API_KEY
from prompts import gpt_assistant_prompt, gpt_user_prompt, gpt_system_prompt

# Load NAICS code mappings and descriptions
def load_naics_data() -> tuple[Dict, Dict]:
    """
    Load NAICS code mappings and descriptions from pickle files.
    
    Returns:
        tuple: (naics_17to22 mapping dict, naics descriptions dict)
    """
    with open("naics_17to22.pkl", "rb") as fr:
        naics_17to22 = pickle.load(fr)
    with open("naics_22.pkl", "rb") as fr:
        naics_desc = pickle.load(fr)
    return naics_17to22, naics_desc

def process_gpt_results(results: List[Dict], 
                       naics_17to22: Dict, 
                       naics_desc: Dict) -> List[Dict]:
    """
    Process GPT results to get filtered and updated NAICS codes.

    Args:
        results: List of raw results from GPT
        naics_17to22: Mapping of old to new NAICS codes
        naics_desc: Dictionary of NAICS code descriptions

    Returns:
        List of filtered results with updated codes and descriptions
    """
    seen = set()
    results_filtered = []

    for result in results:
        naics_code = result["NAICS_code"]
        
        # Update to new NAICS code if available
        if naics_code in naics_17to22:
            naics_code = naics_17to22[naics_code]
        
        # Skip duplicates
        if naics_code in seen:
            continue
            
        description = naics_desc.get(naics_code, result["description"])
        results_filtered.append({
            "NAICS_code": naics_code, 
            "description": description
        })
        seen.add(naics_code)
    
    return results_filtered


def call_search_api(search_api: SearchSerper, search_query: str) -> str:
    """
    Call the search API and display the results in Streamlit.
    """
    try:
        results = search_api.search(search_query)
        context = " ".join(x["body"] for x in results)
        st.write("Search completed!")
                
        if context:
            st.write("Top search results:")
            for result in results:
                st.write(f"Title: {result['title']}")
                st.write(f"Body: {result['body'][:200]}...")
        else:
            st.write("No search results found. Will use knowledge of the LLM.")
    except Exception as e:
        st.error(f"Error: {e}")
        context = ""
        results = []
    return context

def call_gpt(prompt: str, context: str = None):
    """
    Call the GPT API and display the results in Streamlit.
    """
    if not context:
        message = [
            {"role": "system", "content": gpt_system_prompt},
            {"role": "user", "content": gpt_user_prompt.format(prompt)}
        ]
    else:
        message = [
            {"role": "system", "content": gpt_system_prompt},
            {"role": "user", "content": gpt_user_prompt.format(prompt) + f"\nContext: {context}"}
        ]
    
    request_data = {
        'model': 'gpt-4o',
        'messages': message,
        'temperature': 0.001,
        'max_tokens': 300,
        'frequency_penalty': 0.0,
        'n': 3,
        'response_format': {"type": "json_object"},
    }

    # Make GPT API request
    response = requests.post(
        OPENAI_API_URL,
        headers={'Authorization': f'Bearer {OPENAI_API_KEY}'},
        json=request_data
    )
    return response

def main():
    """Main Streamlit application function"""
    # Initialize
    load_dotenv()
    naics_17to22, naics_desc = load_naics_data()
    search_api = SearchSerper()
    st_callback = StreamlitCallbackHandler(st.container())

    # Handle user input
    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        
        with st.chat_message("assistant"):
            # # Search phase
            # with st.spinner("Searching..."):
           

            # GPT processing phase
            st.write("Assistant is thinking...")
            
            response = call_gpt(prompt)
            st.write("Response received!")
            # Handle API response
            if response.status_code == 401:
                st.error("Invalid OpenAI API key")
            else:
                result = response.json()
                if 'search_api' in result['choices'][0]['message']['content']:
                    search_query = json.loads(result['choices'][0]['message']['content'])['search_api']
                    context = call_search_api(search_api, search_query)
                    response = call_gpt(prompt, context)
                    if response.status_code == 401:
                        st.error("Invalid OpenAI API key")
                    else:
                        result = response.json()
                        gpt_results = [json.loads(x['message']['content']) 
                                for x in result['choices']]
                    
                        # Process and display results
                        filtered_results = process_gpt_results(
                            gpt_results, 
                            naics_17to22, 
                            naics_desc
                        )
                        st.write(filtered_results)
                else:
                    gpt_results = [json.loads(x['message']['content']) 
                                for x in result['choices']]
                    
                    # Process and display results
                    filtered_results = process_gpt_results(
                        gpt_results, 
                        naics_17to22, 
                        naics_desc
                    )
                    st.write(filtered_results)

if __name__ == "__main__":
    main()
