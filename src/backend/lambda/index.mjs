import { SageMakerRuntimeClient, InvokeEndpointWithResponseStreamCommand } from "@aws-sdk/client-sagemaker-runtime"


const client = new SageMakerRuntimeClient()


const endpointName = "" // replace with your endpoint

export const handler = awslambda.streamifyResponse(async (event, responseStream, context) => {
  
  responseStream.setContentType('text/event-stream')
  const input = JSON.parse(event.body).input

  const messages = [
    { role: "system", content: "please be helpful" },
    { role: "user", content: input }
  ]
  const payload = {
    messages: messages,
    parameters: {
      do_sample: true,
      max_new_tokens: 1024,
      temperature: 0.2
    },
    stream: true
  };

  const command = new InvokeEndpointWithResponseStreamCommand({
    EndpointName: endpointName, // Replace with actual endpoint name
    ContentType: 'application/json',
    Body: JSON.stringify(payload)
  });

  const sagemakerResponse = await client.send(command);

  for await (const chunk of sagemakerResponse.Body) {
    if (chunk?.PayloadPart?.Bytes) {
      const part = JSON.parse(new TextDecoder().decode(chunk.PayloadPart.Bytes));
      console.log(part)
      const content = part?.choices?.[0]?.delta?.content;
      if (content) {
        responseStream.write(content);
      }
    }
  }

  responseStream.end();
})