import asyncio
from concurrent.futures import Future
from threading import Thread
from typing import Coroutine

from sydney import SydneyClient

class SydneyAsync:
    def __init__(self) -> None:
        self.sydney = SydneyClient(style="precise")

    async def start_sydney_async(self) -> Future:
        await self.sydney.start_conversation()

    async def stop_sydney_async(self) -> Future:
        await self.sydney.close_conversation()

    async def run_sydney_prompt_async(self, prompt, attachment = None) -> Future:
        result = ''
        async for response in self.sydney.ask_stream(prompt, attachment=attachment):
            #print(response, end="", flush=True)
            result += response
        return result

def async_thread(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def run_coro_async(coro:Coroutine, loop) -> Future:
    return asyncio.run_coroutine_threadsafe(coro, loop)
    
def extract_code(input_string):
    start = input_string.find('```python') + 9
    end = input_string.find('```', start)
    if start == -1 or end == -1:
        return ''
    return input_string[start:end]

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    thread = Thread(target=async_thread, args=(loop,), daemon=True)
    thread.start()
    sydney = SydneyAsync()
    run_coro_async(sydney.start_sydney_async(), loop).result()

    async def input_execute():
        print("Welcome, type in your command:")
        while True:
            prompt = input()
            prompt = "No verbose answer, only python code, generate python code for this: " + prompt
            response = await sydney.run_sydney_prompt_async(prompt)
            pythoncode = extract_code(response)
            print(pythoncode)
            if pythoncode == '':
                print("Can't do!")
            else:
                d = dict(locals(), **globals())
                exec(pythoncode, d, d)
            print("Done")

    future = run_coro_async(input_execute(), loop)
    future.result()

    run_coro_async(sydney.stop_sydney_async(), loop).result()