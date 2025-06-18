import chainlit as cl
import json
from google import genai
from google.genai.types import HttpOptions
from googleapiclient.discovery import build
import ollama
from config import Config
from prompts import query_writer_instructions, summarizer_instructions, reflection_instructions
from search_result import SearchResult

def call_llm(prompt = "", system = "", format=None, model=Config.LLM_MODEL_LOW):
    response = ollama.generate(
        model=model,
        prompt=prompt,
        system=system,  
        format=format
    )
    return response.response

def analyze_query(user_prompt):
    response = call_llm(
        model=Config.LLM_MODEL_LOW,
        prompt= "Generate a web query based on the user input: " + user_prompt,      
        system=query_writer_instructions,  
        format= "json"
    )
    return response

def web_search(query):       
    service = build("customsearch", "v1", developerKey=Config.SEARCH_API_KEY)
    res = service.cse().list(
        q=query,
        cx=Config.SEARCH_ENGINE_ID,
        num=5,  # Number of results to return
    ).execute()
    search_results = []
    for item in res.get('items', []):
        search_results.append(SearchResult(
            title=item.get('title', 'No title'),
            link=item.get('link', 'No link'),
            snippet=item.get('snippet', 'No snippet')
        ))
    # Implement web search logic here
    return search_results

def summarize_results(results, research_query, topic, running_summary=None):   
    if running_summary:
        prompt = f"Extend the existing summary: {running_summary} with the new search results {results} on the topic: {research_query}. "
    else:
        prompt="Summarize the following search results: "
        for result in results:
            prompt += f"Link: {result.link}"
        
    response = call_llm(
        model=Config.LLM_MODEL_LOW,
        prompt=prompt,    
        system=summarizer_instructions,
    )

    return response

def reflect_on_summary(query, summary):
    response = call_llm(
        model=Config.LLM_MODEL_LOW,
        system=reflection_instructions.format(query=query),
        prompt=f"Find a weakness or a knowledge gap for the next search based on {summary}",
        format="json"
    )
    return json.loads(response)
        

@cl.on_message
async def main(message: cl.Message):
    analyzed_query = analyze_query(message.content)
    json_query = json.loads(analyzed_query)
    query, topic, reason = json_query['query'], json_query['topic'], json_query['reason']

    running_summary = None

    for i in range(4):

        """
        Main function to handle incoming messages.
        """
        # Process the incoming message
        #await cl.Message(f"Web Query: {query}" ).send()
        await cl.Message( content=f"Optimized Query: {query}\nThinking Topic: {topic}\nReasoning: {reason}", author="system_assistant" ).send()

        search_results = web_search(query)
        formatted_results = ""
        for result in search_results:
            formatted_results += f"\nTitle: {result.title} \nLink: {result.link} \nSnippet: {result.snippet}"    

        summary = summarize_results(search_results, query, topic, running_summary)
        running_summary = summary


        await cl.Message( content=f"Performed web search for: {query} \nFound: {formatted_results}", author="system_assistant" ).send()
        await cl.Message( content=f"Summary of results: {summary}", author="system_assistant" ).send()

        reflected_summary = reflect_on_summary(query, summary)
        query = reflected_summary.get('follow_up_question', f"Tell me more about {topic}")
        knowledge_gap = reflected_summary.get('knowledge_gap', "")

        await cl.Message( content=f"Next search: {query}. I reflected on this because of {knowledge_gap}", author="system_assistant" ).send()