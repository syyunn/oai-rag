# Retrieval Augmented Generation (RAG) Chatbot for multiple PDF files using OpenAI Assitant API

# Retrieval Augmented Generation (RAG)

Retrieval Augmented Generation (RAG) allows the output of a large language model to refer to an external knowledge base outside its training data sources before generating a response. This process ensures that the response is more informative and less prone to hallucination.

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
