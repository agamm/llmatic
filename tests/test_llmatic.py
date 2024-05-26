import openai
from llmatic import track, get_response, llm

def test_llm_call():
    t = track(id="test")
    with llm(retries=3, tracker=t):
        response = openai.Completion.create(
            engine="davinci",
            prompt="Say hello world",
            max_tokens=5,
            n=1,
            stop=None,
            temperature=0.5
        )
    t.end(model="davinci", prompt="Say hello world", response=response)
    assert "Hello, world" in get_response(response)