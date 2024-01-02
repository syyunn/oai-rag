import os
import dotenv

import streamlit as st
from openai import OpenAI
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # if it exists, it's the prod in server

if not OPENAI_API_KEY:  # this is for local dev
    dotenv.load_dotenv(".env")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def main():
  if 'uploaded_button_clicked' not in st.session_state:
    st.session_state['uploaded_button_clicked'] = False
  if 'messages' not in st.session_state:
    st.session_state['messages'] = []
  if 'thread' not in st.session_state:
     st.session_state['thread'] = None
  if 'assistant' not in st.session_state:
     st.session_state['assistant'] = None

  client = OpenAI()

  uploaded_files = st.file_uploader("You can upload multiple PDF files.", 
                                  type=["pdf"], 
                                  accept_multiple_files=True,
                                  label_visibility='visible')


                          
  # Button to trigger the file upload process
  if len(uploaded_files)>0:
    st.write("After uploading all the files, please click the button below to create an assistant to answer questions about the files.")
    if st.button('Upload Files'):
      file_ids = []
      uploaded_logs = []
      st.session_state['uploaded_button_clicked'] = True
      with st.spinner('Uploading Files...'):
        for uploaded_file in uploaded_files:
            # Read the content of the uploaded file
            file_content = uploaded_file.read()

            # Upload a file with an "assistants" purpose
            oai_uploaded_file = client.files.create(
                file=file_content,
                purpose='assistants'
            )
            uploaded_log = {"file_name": uploaded_file.name, "file_id": oai_uploaded_file.id}
            uploaded_logs.append(uploaded_log)
            # st.write(uploaded_log)
            file_ids.append(oai_uploaded_file.id)
        # st.write(uploaded_logs)
            
      with st.spinner('Creating Assistant...'):
        # Add the file to the assistant
        assistant = client.beta.assistants.create(
          instructions=f"""
          You are a helpful assistant to question & answer over multiple files. Here\'s your file_id and file_name mapping:

          {str(uploaded_logs)}

          Please use this mapping to understand which file does the user is referring to.

          [Note]
          If you're asked any question without clear reference to the file name, please answer with the most relevant inferring about which file the user is referring to using the above mapping.
          """,
          model="gpt-4-1106-preview",
          tools=[{"type": "retrieval"}],
          file_ids=file_ids
        )
        st.session_state['assistant'] = assistant
        
        # st.write(st.session_state['assistant'])

        thread = client.beta.threads.create(
          messages=st.session_state.messages
        )

        # st.write(thread)
        st.session_state['thread'] = thread

  # display chat history 
  for message in st.session_state.messages:  # this is to show the chat history
      if message["role"] == "assistant":
          st.chat_message("assistant").write(message["content"])
      else:
          st.chat_message("user").write(message["content"])

  # chat input 
  if st.session_state['assistant']:
    if prompt := st.chat_input(placeholder="Enter your message here"):
        # st.write("prompt", prompt)

        user_message = {
          "role": "user",
          "content": prompt
        }

        # Add the user's response to the chat - frontend
        st.session_state.messages.append(user_message)
        # Add the user's response to the thread - backend
        message = client.beta.threads.messages.create(
            thread_id=st.session_state['thread'].id,
            role="user",
            content=prompt
          )
        
        # display chat
        st.chat_message("user").write(prompt)  # this is to show the user's input

        with st.chat_message("assistant"):
            with st.spinner():
                # Run the assistant
                run = client.beta.threads.runs.create(
                  thread_id=st.session_state['thread'].id,
                  assistant_id=st.session_state['assistant'].id
                )
                
                while run.status != "completed":
                  run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state['thread'].id,
                    run_id=run.id
                  )
  
                url = f"https://api.openai.com/v1/threads/{st.session_state['thread'].id}/messages"

                headers = {'Authorization': f'Bearer {OPENAI_API_KEY}', 
                          'Content-Type': 'application/json', 
                          'OpenAI-Beta': 'assistants=v1'}

                # Send the GET request
                response = requests.get(url, headers=headers)

                # Check the response
                if response.status_code == 200:
                    print("Successfully retrieved data:")
                    print(response.json())
                    # Add the assistant's response to the chat
                    st.session_state.messages.append(
                        {
                          "role": "assistant", 
                          "content": response.json()["data"][0]["content"][0]["text"]["value"]
                        })
                    st.write(response.json()["data"][0]["content"][0]["text"]["value"].replace("$", "\$")) # display the assistant's response

                else:
                    print("Failed to retrieve data. Status code:", response.status_code)
