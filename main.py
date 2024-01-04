import os
import dotenv

import streamlit as st
from openai import OpenAI
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # if the key already exists in the environment variables, it will use that, otherwise it will use the .env file to get the key
if not OPENAI_API_KEY:
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
          """, # instructions to the assistant to understand the context and purpose of the assistant
          model="gpt-4-1106-preview",
          tools=[{"type": "retrieval"}], # augment with your own custom tools!
          file_ids=file_ids
        ) # you need to pass the file_ids as a list when creating the assistant
        st.session_state['assistant'] = assistant
        
        # st.write(st.session_state['assistant'])

        thread = client.beta.threads.create(
          messages=st.session_state.messages
        ) # thread is a collection of messages between the user and the assistant

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
          ) # you can add the user's message to the thread using the thread_id
        
        # display chat
        st.chat_message("user").write(prompt)  # this is to show the user's input

        with st.chat_message("assistant"):
            with st.spinner():
                # Run the assistant
                run = client.beta.threads.runs.create(
                  thread_id=st.session_state['thread'].id,
                  assistant_id=st.session_state['assistant'].id
                ) # after adding the user's message to the thread, you can run the assistant to get the assistant's response
                
                while run.status != "completed":
                  run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state['thread'].id,
                    run_id=run.id
                  ) # you can retrieve the assistant's response when the status is "completed". This part is to make sure that the assistant has completed its response.

                messages = client.beta.threads.messages.list(thread_id=st.session_state['thread'].id)
                assistant_response = messages.data[0].content[0].text.value # get the most recent message
  
                st.session_state.messages.append(
                    {
                      "role": "assistant", 
                      "content": assistant_response # messages are stored in the "data" key with the latest message at the first index
                    })
                st.write(assistant_response.replace("$", "\$")) # display the assistant's response
