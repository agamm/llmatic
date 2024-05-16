# llm-utils
**No BS utilities for developing with LLMs**

### Why?
LLMs are basically API calls that need:
- Swappability
- Rate limit handling
- Visibility on costs, latency and performance
- Response handling

So we are solving those problems exactly without any crazy vendor lock or abstractions ;)


### Examples

Calling an LLM (notice how you can call whatever LLM API you want, you're really free to do as you please).
```py
import openai
from llmutils import track, get_response

# Start tracking an LLM call
t = track(id="story") # llm utils, start tacking an llm call, saved as json files.

# Make the LLM call, note you can use whatever API or LLM you want.
response = openai.Completion.create(
    engine="gpt-4",
    prompt="Write a short story about a robot learning to garden, 300-400 words, be creative.",
    max_tokens=max_tokens,
    n=1,
    stop=None,
    temperature=0.7
)

# End tracking and save call results
t.end(model=model, prompt=prompt, response=response) # Save the cost (inputs/outputs), latency (execution time)

# Evaluation
#  Notice that this acts like the built in `assert`,
#  if you don't want it to affect your runtime in production just use
#  `log_only` (will only track the result) or dev_mode=True (won't run - useful for production).

t.eval("Is the story engaging?", scale=(0,10), "claude-sonnet")
t.eval("Does the story contain the words ['water', 'flowers', 'soil']", scale=(0,10)) # This will use function calling to check "flowers" in story_text_response.
t.eval("Did the response complete in less than 0.5s?", scale=(0,1), log_only=True) # This will not trigger a conditional_retry, just log/track the eval 
t.eval("Was the story between 300-400 words?", scale=(0,1))

# Extract and print the generated text
generated_text = get_response(response) # equivallent to response.choices[0].text.strip()
print(generated_text)
```

### Retries?
Well, we will need to take our relationship to the next level :)

To get the most benefit from llm-utils, we need to wrap all of the relevant LLM calls with a context (`with llm(...)`):
```py
import openai
from llmutils import track, get_response, llm, condition

# Make the API call
t = track(id="story") # llm utils, start tacking an llm call, saved as json files.
with llm(retries=3, tracker=t): # This will also retry any rate limit errors 
  response = openai.Completion.create(
      engine="gpt-4",
      prompt="Write a short story about a robot learning to garden, 300-400 words, be creative.",
      max_tokens=max_tokens,
      n=1,
      stop=None,
      temperature=0.7
  )
t.end(model=model, prompt=prompt, response=response) # Save the cost (inputs/outputs), latency (execution time)

# Eval
t.eval("Was the story between 300-400 words?", scale=(0,1))
t.eval("Is the story creative?", scale=(0,10), "claude-sonnet")
t.conditional_retry(lambda score: score > 7, scale=(0,10), max_retry=3) # If our condition isn't met, retry the llm again
```

### Results (e.g. LangSmith killer)
We use a cli tool to check them out. By default tracking results will be saved under `$HOME/.llmutls/{track_id}/*.json`

- List all trackings: `llmutils list`
- Output the last track `llmutils show <id>` (id="story" in our last example)
Will produce something like:
![image](https://github.com/agamm/llm-utils/assets/1269911/9a81a173-6df3-4084-af78-86e18ef97d1b)


- Compare trackings: `llmutils compare <id> <id2>`
![image](https://github.com/agamm/llm-utils/assets/1269911/f0c4485e-3e57-4c17-b2c9-732e27d4229a)


### Track format

What do trackings look like?
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
You could compare tackings with our CLI *TBD*.

TODO:
- Think about comparing tackings
- Think about tracking agents
- Think about cli utitilies for improveing prompts from the trackings.
- Think of ways to compare different models and prompts in a matrix style for best results using the eval values.
- Github action for eval and results.

### More why?
Most LLM frameworks try to lock you into their ecosystem, which is problematic for several reasons:

- Complexity: Many LLM frameworks are just wrappers around API calls. Why complicate things and add a learning curve?
- Instability: The LLM space changes often, leading to frequent syntax and functionality updates. This is not a solid foundation.
- Inflexibility: Integrating other libraries or frameworks becomes difficult due to hidden dependencies and incompatibilities. You need an agnostic way to use LLMs regardless of the underlying implementation.
- TDD-first: When working with LLMs, it's essential to ensure the results are adequate. This means adopting a defensive coding approach. However, no existing framework treats this as a core value.
- Evaluation: Comparing different runs after modifying your model, prompt, or interaction method is crucial. Current frameworks fall short here (yes, langsmith), often pushing vendor lock-in with their SaaS products.

