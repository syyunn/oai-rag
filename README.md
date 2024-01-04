# RAG Chatbot for Multiple PDFs using OpenAI Assitant API

# Retrieval Augmented Generation (RAG)

Retrieval Augmented Generation (RAG) allows the output of a large language model to refer to an external knowledge base outside its training data sources before generating a response. This process ensures that the response is more informative and less prone to hallucination.

# OpenAI Assistant API

![Agent Image](agent.png)

The LLM Agent elevates the basic LLM by incorporating predefined functions that can be activated to tackle specific problems. This capability empowers the LLM Agent to autonomously select and utilize the most suitable tools to effectively address the problems. In this process, the LLM Agent continuously invokes these functions, supplying appropriate arguments as needed, and then assesses the resulting outputs. Based on these observations, the agent determines the subsequent course of action, continuing this cycle until it deems the problem resolved. Such agent-like abilities are readily accessible through the OpenAI Assistant API, showcasing its versatile problem-solving potential.

# Benefits of OpenAI Assistant API

- The OpenAI Assistant API automatically manages chat history, relieving developers of this concern.
- It supports parallel function calls, eliminating the need for developers to implement such agent-like behavior on their own.
- The API offers RAG capabilities out-of-the-box. Developers don't need to worry about implementing RAG themselves, such as chunking the knowledge base, embedding knowledge, or managing a vector database. All these aspects are automatically handled by the OpenAI Assistant API.

# Run

## Install dependencies

```bash
conda create -n oai-rag python=3.9
conda activate oai-rag
pip install -r requirements.txt
```

## Replace the API key in the .env file

Create a file named `.env` and add the `PENAI_API_KEY` to it.

## Run the app

```bash
sudo hupper -m streamlit run app.py
```
