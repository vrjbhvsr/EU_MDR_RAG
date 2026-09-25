import requests
import json
from src.generation import Prompt_Configuration
from src.utils import log, CustomException
from config.settings import get_settings

class Generate_Answer:
    def __init__(self):
        settings = get_settings()
        self.config = settings.generation
        self.llm_config = settings.llm
        

    def _request(self, prompt: str):
        return requests.post(url=self.config.api,
                             json={"model": self.llm_config.model_name,
                                   "prompt": prompt,
                                   "stream": self.llm_config.stream},
                                   stream= self.llm_config.stream).iter_lines()

    def response(self, prompt: str):
        pieces = ""
        for line in self._request(prompt):
            line = json.loads(line)
            token = line.get('response',"")            
            print(token, end="", flush=True)
            pieces += token
            if line.get('done'):
                break
            #metainfo = {c.get(k) for k in c if k!='response'}
        return {k:line.get(k) for k in line 
                if k in ['total_duration', 'load_duration', 'prompt_eval_count','prompt_eval_duration','eval_count','eval_duration']}


            

                

                



