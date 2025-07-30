#from google import genai
import google.generativeai as genai  # using the deprecated sdk
import time
import os
import json


class GeminiModel:
    def __init__(self, modeltype, key, func=None):
        self.modeltype = modeltype
        self.key = key
        self.num_requests = 0
        self.tokens_used = 0
        self.last_time = time.time()
        self.safety_config = {"HARM_CATEGORY_HARASSMENT": "block_none",
                              "HARM_CATEGORY_DANGEROUS": "block_none",
                              "HARM_CATEGORY_HATE_SPEECH": "block_none",
                              "HARM_CATEGORY_SEXUALLY_EXPLICIT": "block_none"}
        GOOGLE_API_KEY = os.environ.get(self.key)
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.modeltype, safety_settings=self.safety_config) 
        # free tier limits
        if self.modeltype == "gemini-2.5-flash":
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

