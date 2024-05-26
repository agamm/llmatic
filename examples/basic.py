import time
from unittest.mock import Mock
from llmatic import Track, get_response

# Mock the OpenAI API call
mock_openai = Mock()
mock_response = {
    "choices": [{"text": "Once upon a time in a robotic garden..."}]
}
mock_openai.Completion.create.return_value = mock_response

# Start tracking an LLM call
t = Track(id="story", project_id="test01")  # start tracking an LLM call, saved as JSON files.

# Simulate a delay to mock the execution time
time.sleep(0.4)

# Mock the LLM call
response = mock_openai.Completion.create(
    engine="gpt-4",
    prompt="Write a short story about a robot learning to garden, 300-400 words, be creative.",
    max_tokens=400,
    n=1,
    stop=None,
    temperature=0.7
)

# End tracking and save call results
t.end(model="gpt-4", prompt="Write a short story about a robot learning to garden, 300-400 words, be creative.", response=response)  # Save the cost (inputs/outputs), latency (execution time)

# Evaluation
t.eval("Is the story engaging?", scale=(0, 10), model="claude-sonnet")
t.eval("Does the story contain the words ['water', 'flowers', 'soil']", scale=(0, 10))
t.eval("Did the response complete in less than 0.5s?", scale=(0, 1), log_only=True)
t.eval("Was the story between 300-400 words?", scale=(0, 1))

# Extract and print the generated text
generated_text = get_response(response)  # equivalent to response["choices"][0]["text"].strip()
print(generated_text)