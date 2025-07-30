#from google import genai
import google.generativeai as genai
import time
import os
import json


class GeminiModel:
    def __init__(self, modeltype, keys, func=None):
        self.modeltype = modeltype
        self.keys = keys
        self.key = 0
        self.num_requests = 0
        self.tokens_used = 0
        self.last_time = time.time()
        self.safety_config = {"HARM_CATEGORY_HARASSMENT": "block_none",
                              "HARM_CATEGORY_DANGEROUS": "block_none",
                              "HARM_CATEGORY_HATE_SPEECH": "block_none",
                              "HARM_CATEGORY_SEXUALLY_EXPLICIT": "block_none"}
        GOOGLE_API_KEY = os.environ.get(self.keys[self.key])
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.modeltype, safety_settings=self.safety_config) #, tools=[func], tool_config={'function_calling_config':'ANY'})
        if self.modeltype == "gemini-2.0-flash-lite":
            self.rpm = 30
            self.tpm = 1000000
            self.rpd = 200
        elif self.modeltype == "gemini-2.0-flash":
            self.rpm = 15
            self.tpm = 1000000
            self.rpd = 200
        elif self.modeltype == "gemini-2.5-flash":
            self.rpm = 10
            self.tpm = 250000
            self.rpd = 250
        elif self.modeltype == "gemini-2.5-pro":
            self.rpm = 5
            self.tpm = 250000
            self.rpd = 100
        print(f"{self.modeltype} model instantiated")

    def get_response(self, prompt, config=None):
        # make sure not to go over model limitations
        now = time.time()
        if (self.num_requests % self.rpm == self.rpm - 1) and (now - self.last_time) >= 60:
            time.sleep(60)
            self.last_time = time.time()
        self.tokens_used += self.model.count_tokens(prompt).total_tokens
        if (self.tokens_used > self.tpm) and (now - self.last_time) >= 60:
            time.sleep(60)
            self.tokens_used = 0
            self.last_time = time.time()
        if self.num_requests == self.rpd:
            print(f"Out of requests per day, switching keys to {self.key + 2}")
            self.key += 1
            if self.key + 1 > len(self.keys):
                print("Out of calls")
                exit()
            GOOGLE_API_KEY = os.environ.get(self.keys[self.key])
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(self.modeltype, safety_settings=self.safety_config)
        if config is not None:
            response = self.model.generate_content(prompt, generation_config=config)
        else:
            response = self.model.generate_content(prompt)
        response = response.text
        # check token usage also after generation
        now = time.time()
        self.tokens_used += self.model.count_tokens(response).total_tokens
        if (self.tokens_used > self.tpm) and (now - self.last_time) >= 60:
            time.sleep(60)
            self.tokens_used = 0
            self.last_time = time.time()
        self.num_requests += 1
        return response

