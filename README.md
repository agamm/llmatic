# llm-utils
No BS utitilies for developing with LLMs


### Why?
Most LLM frameworks try to lock you into their ecosystem, which is problematic for several reasons:

- Complexity: Many LLM frameworks are just wrappers around API calls. Why complicate things and add a learning curve?
- Instability: The LLM space changes often, leading to frequent syntax and functionality updates. This is not a solid foundation.
- Inflexibility: Integrating other libraries or frameworks becomes difficult due to hidden dependencies and incompatibilities. You need an agnostic way to use LLMs regardless of the underlying implementation.
- TDD-first: When working with LLMs, it's essential to ensure the results are adequate. This means adopting a defensive coding approach. However, no existing framework treats this as a core value.
- Evaluation: Comparing different runs after modifying your model, prompt, or interaction method is crucial. Current frameworks fall short here (yes, langsmith), often pushing vendor lock-in with their SaaS products.
- 
### Features
- LLM/API-agnostic
- Track Costs
- Track Performance (quality of result)
- Track Latency
- Evaluation reports and comparison
- Many utility functions to deal with responses, rate limits, and retries

### Examples

Calling an LLM (notice how you can call what ever LLM api you want, you're really free to do as you please).
```py
import openai
from llmutils import track, get_response, retry, condition

# Define the prompt and parameters
prompt = "Write a short story about a robot learning to garden, 300-400 words, be creative."
model = "gpt-4" 

# Make the API call
t = track(id="story") # llm utils, start tacking an llm call, saved as json files.
with retry(retries=3): # llm utils retry
  response = openai.Completion.create(
      engine=model,
      prompt=prompt,
      max_tokens=max_tokens,
      n=1,
      stop=None,
      temperature=0.7
  )
t.end(model=model, prompt=prompt, response=response) # Save the cost (inputs/outputs), latency (execution time)

# Evaluation
# Notice that this acts like the built in `assert`, if you don't want it to affect your runtime in production just use `log_only` (will only track the result) or dev_mode=True (won't run - useful for production).
t.eval("Is the story engaging?", scale=(0,10), "claude-sonnet")
t.eval("Does the story contain the words ['water', 'flowers', 'soil']", scale=(0,10)) # This will use function calling to check "flowers" in story_text_response.
t.eval("Did the response complete in less than 0.5s?", scale=(0,1), log_only=True) # This will not trigger a conditional_retry, just log/track the eval 
t.eval("Was the story between 300-400 words?", scale=(0,1))
t.conditional_retry(lambda score: score < 7, normalize_score=(0,10)) # will call the completion again if the evals don't pass our threashold

# Extract and print the generated text
generated_text = get_response(response) # equivallent to response.choices[0].text.strip()
print(generated_text)
```

How do trackings look like?
They are just json files like so:
```json
{
  "id": "story",
  "execution_time_ms": 564,
  "input": [...],
  "output": [...],
  "eval_results": {
    "total": 8.7,
    "engagement": 8, ...
  },
  "created_at": ...
}
```
You could comapre tackings with our CLI.

TODO:
- Think about comparing tackings
- Think about tracking agents
- Think about cli utitilies for improveing prompts from the trackings.
- Think of ways to compare different models and prompts in a matrix style for best results using the eval values.
