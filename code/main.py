from llm import *
from generate_cases import *
from automodel import *
from evaluate import *
from analysis import *
import json
import os




if __name__ == "__main__":

    #"""
    keys = [#os.environ.get('GOOGLE_API_KEY1'),
            #os.environ.get('GOOGLE_API_KEY2'),
            #os.environ.get('GOOGLE_API_KEY3'),
            os.environ.get('GOOGLE_API_KEY4'),
            os.environ.get('GOOGLE_API_KEY5'),
            ]

    #agent = GeminiModel("gemini-2.0-flash-lite", keys)
    #agent = GeminiModel("gemini-2.5-flash", keys)
    agent = GeminiModel("gemini-2.5-pro", keys)
    #"""

    """
    categories = ["predator-prey",
                  "mating-partner-selection",
                  "symbiotic-cooperation",
                  "social-foraging",
                  "habitat-selection"]
    for category in categories:
        print("processing category: ", category)
        cases = get_cases(agent, category)
        with open(category+".json", "w") as f:
            json.dump(cases, f, indent=4)
    """

    """
    # iterate over categories
    files = ['predator-prey.json',
             'mating-partner-selection.json',
             'symbiotic-cooperation.json',
             'social-foraging.json',
             'habitat-selection.json']
    for filename in files:
        print(filename)
        with open(filename) as f:
            category = json.load(f)
        #category = get_wiki_articles(agent, category)
        #category = autoformalize_category(agent, category)
        #category = expected_outcomes_category(agent, category)
        category = validate_category_semantic(agent, category)
        #category = update_category(agent, category)
        if category is not None:
            with open(filename, "w") as f:
                json.dump(category, f, indent=4)
    """

    #"""
    # iterate over categories
    files = [#'predator-prey',
             #'mating-partner-selection',
             #'symbiotic-cooperation',
             'social-foraging',
             #'habitat-selection'
            ]
    for filename in files:
        print(filename)
        with open(filename + ".json") as f:
            category = json.load(f)
        #category = validate_category(category)
        #category = solve_category(category)
        #category = get_stats_feedback(category, numpass=1)
        validated = collect_validated_games(category)
        print("validated: ", len(validated))
        validated = analyze_validated_set(agent, validated)
        if validated is not None:
            with open(filename + "-analysis.json", "w") as f:
                json.dump(validated, f, indent=4)
    #"""
