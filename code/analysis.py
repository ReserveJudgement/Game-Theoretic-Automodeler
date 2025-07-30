import json

def collect_validated_games(category):
    validated = []
    for i, item in enumerate(category):
        if "Game" in list(item.keys()):
            for game in item["Game"]:
                if ("Validated" in list(game.keys())) and (game["Validated"] is True) and ("Error" not in list(game.keys())) and ("Equilibria" in list(game.keys())) and (len(game["Equilibria"]["Support"]) == len(game["Equilibria"]["Vertex"]) == 1):
                    validated.append({"Game_Num": i,
                                      "Description": "Background:\n" + item["Article"] + "\n\nInteraction of interest:\n" + item["Description"],
                                      "Outcome": item["Outcome"],
                                      "Game": game["GameDef"],
                                      "Equilibria": game["Equilibria"]})
    return validated


def experiment_design(agent, description, outcome, game):
    try:
        # Prepare the prompt for the Gemini model.
        prompt = """
        You are an expert biologist. 
        You are provided with the description of an animal interaction and a formal game definition in JSON format. 
        The game is a hypothesized model of the animal behaviors. 
        The Nash equilibrium of the game fits the most commonly observed outcome of the animal interaction.
        But we want to know how predictive the game model is of the animal behaviors more generally.
        Your task is to design either a lab experiment or a field study that tests the accuracy of the game model under alternative conditions.
        
        Elements of the study that need to be planned:
        - Goal: succinct formulation of the purpose of the study.
        - Hypothesis: precise definition of the independent and dependent variables, the null hypothesis and the hypothesis.
        - Type: whether it's a lab experiment or field study.
        - Method: the intervention or manipulation in the lab, or the means of observation in the field.
        - Requirements: the tools, instruments or other preconditions for carrying out the study.
        - Data: the observations to be collected and their format.
        - Ethics: ethical considerations in the study design.
        
        Use the following JSON schema:  

        ```json
        {"Goal": str , "Hypothesis": str, "Type": str ("lab" or "field"), "Method": str, "Instruments": str, "Data": str, "Ethics": str}
        ```
 
        """

        prompt += f"""\nDescription:\n{description}\n\nUsual Observation:\n{outcome}\n\nGame Model:\n{game}\n\n
        
        Respond ONLY with the JSON string for the proposed study.
        """

        response = agent.get_response(prompt)

        # parse
        response_json = response.split("```json")[-1].split("```")[0]
        response_json = json.loads(response_json)
        return response_json

    except Exception as e:
        print(f"Error during autoformalization: {e}")
        return None



def theoretical_analysis(agent, games):
    try:
        # Prepare the prompt for the Gemini model.
        prompt = """
        You are an expert game theorist. 
        You are provided with a set of formal game definitions in JSON format. 
        They are normal-form two-player games.
        Your task is to analyze the games and characterize them using game theoretic concepts.
        For example:
        - Are the games cooperative, competitive or mixed games?
        - Are the utilities symmetric or asymmetric?
        - Are there dominant strategies?
        - Are the equilibria strategies pure or mixed?
        - Do they fall into certain categories of well-studied games (such as prisoner's dilemma etc.)?
        - Do the game structures have striking commonalities or patterns?
        
        """

        prompt += f"""\nGame Definitions:\n{games}\n\n

        Respond with a thorough and professional game-theoretic analysis.
        """

        response = agent.get_response(prompt)

        return response

    except Exception as e:
        print(f"Error during autoformalization: {e}")
        return None


def analyze_validated_set(agent, validated):
    for i, item in enumerate(validated):
        description = item["Description"]
        outcome = item["Outcome"]
        game = item["Game"]
        proposal = experiment_design(agent, description, outcome, game)
        if proposal is not None:
            validated[i]["ProposedStudy"] = proposal
    analysis = theoretical_analysis(agent, validated)
    print(analysis)
    return validated, analysis
