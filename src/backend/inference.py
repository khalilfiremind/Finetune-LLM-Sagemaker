import os
import io
import json
import boto3

PROFILE_NAME = 'dev'
REGION_NAME = "us-east-1"
ENDPOINT_NAME = "webinar-model-endpoint-VLLM-1747432398"


# Create a Boto3 session using the specified profile
boto3_session = boto3.Session(profile_name=PROFILE_NAME, region_name=REGION_NAME)

# Initialize the SageMaker session with the Boto3 session
sagemaker_runtime = boto3_session.client('sagemaker-runtime')

class LineIterator:
    """
    A helper class for parsing the byte stream input. 
    
    The output of the model will be in the following format:
    ```
    b'{"outputs": [" a"]}\n'
    b'{"outputs": [" challenging"]}\n'
    b'{"outputs": [" problem"]}\n'
    ...
    ```
    
    While usually each PayloadPart event from the event stream will contain a byte array 
    with a full json, this is not guaranteed and some of the json objects may be split across
    PayloadPart events. For example:
    ```
    {'PayloadPart': {'Bytes': b'{"outputs": '}}
    {'PayloadPart': {'Bytes': b'[" problem"]}\n'}}
    ```
    
    This class accounts for this by concatenating bytes written via the 'write' function
    and then exposing a method which will return lines (ending with a '\n' character) within
    the buffer via the 'scan_lines' function. It maintains the position of the last read 
    position to ensure that previous bytes are not exposed again. 
    """
    
    def __init__(self, stream):
        self.byte_iterator = iter(stream)
        self.buffer = io.BytesIO()
        self.read_pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.buffer.seek(self.read_pos)
            line = self.buffer.readline()
            if line and line[-1] == ord('\n'):
                self.read_pos += len(line)
                return line[:-1]
            try:
                chunk = next(self.byte_iterator)
            except StopIteration:
                if self.read_pos < self.buffer.getbuffer().nbytes:
                    continue
                raise
            if 'PayloadPart' not in chunk:
                print('Unknown event type:' + chunk)
                continue
            self.buffer.seek(0, io.SEEK_END)
            self.buffer.write(chunk['PayloadPart']['Bytes'])

def get_model_response(user_input):
    messages = [
        {"role": "system", "content": "please be helpful"},
        {"role": "user", "content": user_input}
    ]

    payload = {
        "messages": messages,
        "parameters": {
            "do_sample": True,
            "max_new_tokens": 2048,
            "temperature": 0.2,
            "stop": [ "<|start_header_id|>", "<|end_header_id|>", "<|eot_id|>" ]
        },
        "stream": True
    }

    print("\nAI: ", end='', flush=True)  # Print AI: prefix and flush immediately
    
    response = sagemaker_runtime.invoke_endpoint_with_response_stream(
        EndpointName=ENDPOINT_NAME, 
        Body=json.dumps(payload), 
        ContentType="application/json"
    )
    event_stream = response['Body']

    try:
        for line in LineIterator(event_stream):
            resp = json.loads(line)
            content = resp.get("choices")[0].get('delta').get('content', '')
            if content:
                print(content, end='', flush=True)  # Print each token and flush immediately
        print()  # Add a newline after the response
    except Exception as e:
        print(f"\nError during streaming: {str(e)}")

def main():
    print("Welcome to the AI Chat Interface!")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            get_model_response(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()