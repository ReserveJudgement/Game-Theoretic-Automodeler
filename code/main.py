from llm import *
from generate_cases import *
from automodel import *
from evaluate import *
from analysis import *
import json
import os




if __name__ == "__main__":

    key = os.environ.get('GOOGLE_API_KEY')
    agent = GeminiModel("gemini-2.5-flash", key)
    
    # Generate cases
    categories = ["predator-prey",
                  "symbiotic-cooperation",
                  "social-foraging",
                  "habitat-selection"]
    for category in categories:
        print("processing category: ", category)
        cases = get_cases(agent, category)
        with open(category+".json", "w") as f:
            json.dump(cases, f, indent=4)
    
"""
    # Get Wikipedia articles and automodel
    files = ['predator-prey',
             'mating-partner-selection',
             'symbiotic-cooperation',
             'social-foraging',
             'habitat-selection']
    for filename in files:
        print(filename)
        with open(filename+".json") as f:
            category = json.load(f)
        #category = get_wiki_articles(agent, category) # Get Wikipedia articles
        #category = autoformalize_category(agent, category) # Automodel cases (generate games)
        #category = expected_outcomes_category(agent, category) # Formalize the observed outcomes in nature
        #category = validate_category_semantic(agent, category) # Semantic validation
        #category = update_category(agent, category) # Update when there is feedback
        if category is not None:
            with open(filename+".json", "w") as f:
                json.dump(category, f, indent=4)
    

    # Game theoretic validation
    # iterate over categories
    files = ['predator-prey',
             'symbiotic-cooperation',
             'social-foraging',
             'habitat-selection'
            ]
    for filename in files:
        print(filename)
        with open(filename + ".json") as f:
            category = json.load(f)
        #category = validate_category(category) # Syntactic validation
        #category = solve_category(category) # Solve nash equilibria and check if outcome is in them
        #category = get_stats_feedback(category, numpass=1) # Get statistics on success rates by pass number
        if category is not None:
            with open(filename + ".json", "w") as f:
                json.dump(category, f, indent=4)
        
    # Analysis stage
    files = ['predator-prey',
         'symbiotic-cooperation',
         'social-foraging',
         'habitat-selection'
        ]
    for filename in files:
        print(filename)
        with open(filename + ".json") as f:
            category = json.load(f)
        #validated = collect_validated_games(category) # Concentrate validated game models into one file
        #validated = analyze_validated_set(agent, validated) # Perform analysis on validated game models
        if validated is not None:
            with open(filename + ".json", "w") as f:
                json.dump(validated, f, indent=4)
        
"""
