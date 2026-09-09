from groq import Groq
import os
import json
MEMORY_FILE = "agent_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(user_input, answer, lesson):
    memory = load_memory()
    memory.append({"question": user_input, "answer": answer, "lesson": lesson})
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

client = Groq(api_key=os.environ["GROQ_API_KEY"])
def reflect(user_input, answer):
    reflection_prompt = f"""Topic asked: {user_input}
    Explanation given: {answer}
    
    In one sentence, note what kind of explanation style would help this student understand better next time (e.g. needs more examples, needs simpler language, understood quickly)."""
def run_agent(user_input):
    memory = load_memory()
    memory_text = "\n".join(f"Q: {m['question']} A: {m['answer']}" for m in memory[-5:])

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        message=[
{"role": "system", "content": f"You are a patient tutor. Past lessons about this student's learning style:\n{memory_text}\nAdjust your explanation style accordingly."}
        ]
        ,
        tools=tools
    )
    message = response.choices[0].message

    if message.tool_calls:
        call = message.tool_calls[0]
        args = json.loads(call.function.arguments)
        result = calculator(args["expression"])
        answer = f"[Used calculator] Result: {result}"
    else:
        answer = message.content

    lesson=reflect(user_input,answer)
    save_memory(user_input, answer, lesson)
    return answer

def calculator(expression):
    try:
        return str(eval(expression))
    except:
        return "Error: invalid expression"

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluates a math expression, e.g. '5*12'",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }
]

MEMORY_FILE = "agent_memory.json"

def run_agent(user_input):
    memory = load_memory()
    memory_text = "\n".join(f"Q: {m['question']} A: {m['answer']}" for m in memory[-5:])

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": f"Past conversation history:\n{memory_text}"},
            {"role": "user", "content": user_input}
        ],
        tools=tools
    )
    message = response.choices[0].message

    if message.tool_calls:
        call = message.tool_calls[0]
        args = json.loads(call.function.arguments)
        result = calculator(args["expression"])
        answer = f"[Used calculator] Result: {result}"
    else:
        answer = message.content
    lesson = reflect(user_input, answer)
    save_memory(user_input, answer, lesson)
    return answer
# Chat loop
if __name__ == "__main__":
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        answer = run_agent(user_input)
        print("Agent:", answer)