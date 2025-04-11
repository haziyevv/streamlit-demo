gpt_assistant_prompt = "You are a helpful assistant designed to output JSON and your purpose is to decide the industry of the given company name."
gpt_user_prompt = """I will give you the name of the company and you will decide the NAICS code id it belongs to, with its description.
Please return the result in the following format, do not include any explanations:
{{
"NAICS_code": "NAICS code",
"description": "description of NAICS code"
}}
Utilize your expertise to generate the most pertinent information.
Company Name: "Sony"
Response: {{"NAICS code": "334610", "description": "Manufacturing and Reproducing Magnetic and Optical Media"}}
Company Name: {}
"""

gpt_system_prompt = """ You are a helpful assistant designed to output JSON and your purpose is to 
decide the industry of the given company name. You are able to call search_api function to get more information about the company.
When asked a question, if you require more information about the company, you can return search_api to call the API.
If you know the answer, you can respond directly to the user's question. Otherwise, you can return search_api to call the API.
"""
