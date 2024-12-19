import time

def create_assistant(client, name, instructions, files=None):

    if files:


        vector_store = client.beta.vector_stores.create(name="vector_store_1")
        
        file_streams = [prepare_file(client, f).id for f in files]

        print(vector_store.id)
                
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=[vector_store.id], file_ids=[file for file in file_streams]
        )

        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model="gpt-4-1106-preview",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            },
        )

        return assistant

    else:

        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model="gpt-4-1106-preview",
        )
    
        return assistant

def prepare_file(client, path):
    file = client.files.create(
        file=path,
        purpose='assistants'
    )
    return file

def create_thread(client):
    thread = client.beta.threads.create()
    
    return thread

def send_message(client, thread, user_message):
    
    message = client.beta.threads.messages.create(
        thread_id = thread.id,
        role="user",
        content=user_message
    )
    
    log = last_message(client, thread)
    
    return message, log

def start_run(client, thread, assistant):
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        model="gpt-4-1106-preview",
        tools=[{"type": "file_search"}]
    )
    
    return run

def retrieve_run(client, thread, run):
    
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    
    return run

def generate_response(client, thread, assistant):
    run = start_run(client, thread, assistant)

    while run.status != 'completed':
        run = retrieve_run(client, thread, run)
        time.sleep(0.5)
        
    log = last_message(client, thread)
        
    return run, log

def last_message(client, thread):
    messages = client.beta.threads.messages.list(
      thread_id=thread.id
    )
    last_msg = messages.dict()['data'][0]
    
    role = last_msg['role']
    content = last_msg['content'][0]['text']['value']
    
    return {'role': role, 'content': content}
