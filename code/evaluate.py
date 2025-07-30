import json
import nashpy as nash
import numpy as np
from typing import Dict, Any, Tuple, List, Union


def validate_game_semantic(agent, description, game):
    # check that utilities make semantic sense (death is low, eating or mating is high etc.)
    # check that expected outcome matches description
    try:
        prompt = f"""You are an experienced biologist. 
        You are provided with a textual description of an animal interaction and a JSON string defining a formal game that models this interaction.
        Your task is to validate the *semantic* correctness of the formal game definition.
        For your answer, use the text description given, your background knowledge and common sense.
        When checking the validity of the game, make sure that the action definitions and the numeric utilities are biologically plausible for the respective species.
        However, do not add any extra players. We wish to restrict ourselves to two-animal interactions only.
        Here are some examples of potential issues:
        1. Orders of preferences should make sense, e.g. a player being eaten by a predator should have the lowest utility for that player.
        2. The player actions defined should be mutually exclusive, i.e. the animal is not capable of choosing more than one of the actions in the given situation.
        3. The game is not trivial or degenerate, e.g. the animal is not indifferent to its choices. 
        4. The game has high fidelity to the natural world, i.e. there are no made-up behaviors that don't exist in the description or in nature.

        Interaction of interest: {description}

        Game definition: {game}
        
        Your output should be a detailed comment on what to change and why.
        If the game is fine as is and requires no change, just output: "None".
        """

        response = agent.get_response(prompt)

        return response

    except Exception as e:
        comment = f"Error during semantic validation: {e}"
        print(comment)
        return None


def update_game_comment(agent, game, comment):
    # check that utilities make semantic sense (death is low, eating or mating is high etc.)
    # check that expected outcome matches description
    for i in range(2):
        try:
            prompt = f"""You are an experienced game formalization assistant. 
            You are provided with a JSON string defining a formal game and comments for game improvement.
            Your task is to implement the comments and produce an updated game. 
            Use precisely the same format as the original game, but with the specific modifications requested.
            
            Game description: {game}
            
            Modifications to implement: {comment}
            
            Remember to stick to the original JSON schema: a *list* of dicts, in which each dict contains information about a player (name, actions, utilties), exactly as in the game description above.
            If the game is fine as is and requires no change, just return an empty list [].
            """

            response = agent.get_response(prompt)

            # parse
            response_json = response.split("```json")[-1].split("```")[0]
            response_final = json.loads(response_json)
            break
        except Exception as e:
            comment = f"Error during semantic validation: {e}"
            game = response
            print(comment)
            response_final = None
    return response_final


def validate_category_semantic(agent, category):
    modifications = 0
    for i, item in enumerate(category):
        print("processing ", i+1)
        if "Game" in list(item.keys()):
            description = item["Description"]
            game = json.dumps(item["Game"][-1]["GameDef"])
            comment = validate_game_semantic(agent, description, game)
            if comment is not None and comment.lower() != "none":
                newgame = update_game_comment(agent, game, comment)
                if newgame is not None and newgame != []:
                    category[i]["Game"][-1]["SemanticFeedback"] = comment
                    # make sure new game is valid
                    valid, message = validate_game_formal(newgame)
                    if valid is True:
                        category[i]["Game"][-1]["OldGame"] = category[i]["Game"][-1]["GameDef"]
                        category[i]["Game"][-1]["GameDef"] = newgame
                        print("game updated")
                        modifications += 1
                    else:
                        print("invalid game proposed: ", message)
                        print("trying to fix...")
                        newgame = update_game_comment(agent, newgame, message)
                        if newgame is not None and newgame != []:
                            valid, message = validate_game_formal(newgame)
                            if valid is True:
                                category[i]["Game"][-1]["OldGame"] = category[i]["Game"][-1]["GameDef"]
                                category[i]["Game"][-1]["GameDef"] = newgame
                                print("game updated")
                                modifications += 1
                            else:
                                category[i]["Game"][-1]["ProposedGame"] = newgame
                                category[i]["Game"][-1]["SemanticFeedback"] = f"New proposed game was not formally valid: {message}"
    print("modifications: ", modifications)
    return category


def validate_game_formal(game_data: list) -> Tuple[bool, str]:
    """
    Validates a game JSON object against the specified schema,
    checking for numeric utility values and action/response consistency.
    Supports more than two players.

    Args:
        game_data: A JSON object representing the game state.

    Returns:
        A tuple: (True, "Validation successful") if the JSON is valid,
                 or (False, error_message) if invalid.
    """

    # Check for the correct structure (players, actions, responses).
    if not isinstance(game_data, list):
        return False, "Invalid game data structure: must be a list."

    if len(game_data) < 2:
        return False, "Invalid game data structure: two players required."

    if len(game_data) > 2:
        return False, "Only accepting 2 player games for now."

    for player in game_data:
        if not isinstance(player, dict):
            return False, f"Invalid game data structure: Player '{player['name']}' has invalid structure, must be dict."

    # Helper function to validate utility values
    def validate_utilities(actions: Dict[str, Any], player_name: str) -> Tuple[bool, str]:
        for action, action_data in actions.items():
            if not isinstance(action_data, dict):
                return False, f"Invalid format: action '{action}' for {player_name} must be a dict"

            for response, utility in action_data.items():
                if not isinstance(utility, dict):
                    return False, f"Invalid response format: response '{response}' for {player_name} action '{action}' must be a dict"

                if not isinstance(utility['utility'], int) and not isinstance(utility['utility'], float):
                    return False, f"Invalid utility value: utility for {player_name} action '{action}' given response '{response}' must be numeric."
        return True, ""  # Success

    # Check numeric utility values
    for player_name, actions in [(x['name'], x['utilities']) for x in game_data]:
        valid, error_message = validate_utilities(actions, player_name)
        if not valid:
            return False, error_message

    # Check action/response consistency.
    responses = {}
    for player in game_data:
        all_responses = [list(player['utilities'][action].keys()) for action in player['actions']]
        if not all([all_responses[x] == all_responses[0] for x in range(len(all_responses))]):
            return False, f"Not all responses equivalent across actions for player {player['name']}"
        responses[player['name']] = all_responses[0]
        # compare responses to actions of other player
        for other_player in game_data:
            if other_player['name'] != player['name']:
                if not all([x in other_player['actions'] for x in responses[player['name']]]):
                    return False, f"Inconsistent actions and responses.  Player {player['name']}'s responses do not match the actions of {other_player['name']}.\nresponses{responses}\nactions:{other_player['actions']}"

    return True, "Validation successful"


def validate_category(category):
    for i, item in enumerate(category):
        print("game ", i+1)
        if "Game" in list(item.keys()):
            for numpass in range(len(item["Game"])):
                valid, message = validate_game_formal(item["Game"][numpass]["GameDef"])
                print(valid, message)
                if valid is False:
                    category[i]["Game"][numpass]["Error"] = message
                elif valid is True and "Error" in list(item["Game"][numpass].keys()):
                    category[i]["Game"][numpass].pop("Error")
        else:
            print("No game in ", i)
    return category


def create_nashpy_game(game_data: dict) -> Tuple[Union[nash.Game, None], str]:
    """
    Converts a game JSON object into a Nashpy game object.

    Args:
        game_data: A JSON object representing the game state.

    Returns:
        A tuple: (nashpy.Game object, "Success") if successful,
                 or (None, error_message) if an error occurs.
    """

    # Create utility matrices
    utility_matrices: List[np.ndarray] = []
    for player in game_data:
        utilities = []
        # Populate the utility matrix
        for action in player["actions"]:
            for other_player in game_data:
                if player["name"] != other_player["name"]:
                    utilities.append([player["utilities"][action][response]["utility"] for response in other_player["actions"]])

        utility_matrix = np.array(utilities)
        utility_matrices.append(utility_matrix)

    # make sure it's a two player game
    try:
        assert len(utility_matrices) ==2
    except Exception as e:
        "Error setting up utilities: not a two player game"

    utility_matrices[1] = utility_matrices[1].transpose()

    # Create the Nashpy game object
    try:
        game = nash.Game(*utility_matrices)
    except Exception as e:
        message = f"Error creating Nashpy game: {e}"
        print(message)
        return None, message

    return game, "Success creating Nashpy game"


def calaculate_nash_equilibria(json_def, game):
    support = []
    vertex = []
    lemke_hawson = []
    message = ""
    try:
        for eq in game.support_enumeration():
            support.append({json_def[0]["name"]: {json_def[0]["actions"][x]: abs(round(eq[0][x], 2)) for x in range(len(eq[0]))},
                            json_def[1]["name"]: {json_def[1]["actions"][x]: abs(round(eq[1][x], 2)) for x in range(len(eq[1]))}})
    except Exception as e:
        message += "Support algorithm failed. "
    try:
        for eq in game.vertex_enumeration():
            vertex.append({json_def[0]["name"]: {json_def[0]["actions"][x]: abs(round(eq[0][x], 2)) for x in range(len(eq[0]))},
                           json_def[1]["name"]: {json_def[1]["actions"][x]: abs(round(eq[1][x], 2)) for x in range(len(eq[1]))}})
    except Exception as e:
        message += "Vertex algorithm failed. "
    try:
        for eq in game.lemke_howson_enumeration():
            lemke_hawson.append({json_def[0]["name"]: {json_def[0]["actions"][x]: abs(round(eq[0][x], 2)) for x in range(len(eq[0]))},
                                 json_def[1]["name"]: {json_def[1]["actions"][x]: abs(round(eq[1][x], 2)) for x in range(len(eq[1]))}})
    except Exception as e:
        message += "Lemke-Hawson algorithm failed. "

    # prepare for comparisons
    support_json = [json.dumps(x, sort_keys=True) for x in support]
    vertex_json = [json.dumps(x, sort_keys=True) for x in vertex]
    lemke_hawson_json = [json.dumps(x, sort_keys=True) for x in lemke_hawson]
    lemke_hawson_json = list(set(lemke_hawson_json))
    lemke_hawson = [json.loads(x) for x in lemke_hawson_json]

    try:
        assert all([x in support_json for x in lemke_hawson_json])
        assert all([x in vertex_json for x in lemke_hawson_json])
    except Exception as e:
        message += "Equilibrium found in Lemke-Hawson that isn't in Support or Vertex. "
    try:
        assert all([x in support_json for x in vertex_json])
        assert all([x in vertex_json for x in support_json])
    except Exception as e:
        message += "Equilibria in Support and Vertex not equivalent. "
    message += f"{len(support)} equilibria found in Support. "
    message += f"{len(vertex)} equilibria found in Vertex. "
    return support, vertex, lemke_hawson, message


def solve_category(category):
    for i, item in enumerate(category):
        print("game", i+1)
        if "Game" in list(item.keys()):
            for numpass in range(len(item["Game"])):
                val = 0
                if "Error" not in list(item["Game"][numpass].keys()):
                    game_object, message = create_nashpy_game(item["Game"][numpass]["GameDef"])
                    print(message)
                    if game_object is None:
                        category[i]["Game"]["Error"] = message
                    elif game_object is not None:
                        equilibria_sup, equilibria_vtx, equilibria_lh, message = calaculate_nash_equilibria(item["Game"][numpass]["GameDef"], game_object)
                        category[i]["Game"][numpass]["Equilibria"] = {}
                        category[i]["Game"][numpass]["Equilibria"]["Support"] = equilibria_sup
                        category[i]["Game"][numpass]["Equilibria"]["Vertex"] = equilibria_vtx
                        category[i]["Game"][numpass]["Equilibria"]["LemkeHawson"] = equilibria_lh
                        category[i]["Game"][numpass]["Equilibria"]["Comments"] = message
                        print(message)
                        # Now check if outcome in equilibria
                        equivalent = False
                        print("checking if outcome in equilibrium")
                        outcome = item["Outcome"]
                        eq = equilibria_sup
                        players = [x["name"] for x in item["Game"][numpass]["GameDef"]]
                        if all([x in players for x in list(outcome.keys())]):
                            # check if outcome in equilibria
                            eqs = [{p: max(eq[x][p], key=eq[x][p].get) for p in players} for x in range(len(eq))]
                            if all([outcome[x] in [best_response[x] for best_response in eqs] for x in players]):
                                equivalent = True
                                val += 1
                        category[i]["Game"][numpass]["Validated"] = equivalent
            print(f"Outcome found in equilibria in {val} games")
    return category


def get_stats_feedback(category, numpass=0):
    total = 0
    failed_article = 0
    failed_gamegen = 0
    syntactic_error = 0
    semantic_update = 0
    validated = 0
    degenerate = 0
    multieq = 0
    notineq = 0
    single_valid = 0
    for i, item in enumerate(category):
        feedback = ""
        if "Game" not in list(item.keys()):
            if item["Article"] == "Error":
                failed_article += 1
            else:
                failed_gamegen += 1
        else:
            if len(item["Game"]) > numpass:
                total += 1
                game = item["Game"][numpass]
                if "GameDef" not in list(game.keys()):
                    failed_gamegen += 1
                else:
                    if "Error" in list(game.keys()) and "Equilibria" not in list(game.keys()):
                        syntactic_error += 1
                        feedback += "Technical errors: " + game["Error"]
                    if "SemanticFeedback" in list(game.keys()) and "PrevGame" in list(game.keys()):
                        semantic_update += 1
                    if "Equilibria" in list(game.keys()) and "Validated" in list(game.keys()):
                        if game["Validated"] is True or game["Validated"] == "True":
                            if (len(game["Equilibria"]["Support"]) % 2 == 0) or (len(game["Equilibria"]["Support"]) != len(game["Equilibria"]["Vertex"])):
                                degenerate += 1
                                feedback += "The game might be degenerate. Check if one or both players are indifferent to their strategies. "
                            else:
                                validated += 1
                                if len(game["Equilibria"]["Support"]) > 1:
                                    multieq += 1
                                    feedback += "The game has multiple equilibria. A game with a more definite outcome would be better. "
                                elif len(game["Equilibria"]["Support"]) == 1:
                                    single_valid += 1
                                    feedback = "None"
                        elif game["Validated"] is False or game["Validated"] == "False":
                            notineq += 1
                            feedback += "The naturally observed outcome of the interaction is not an equilibrium in the game! "

                if feedback == "":
                    feedback = "None"
                category[i]["Game"][numpass]["Feedback"] = feedback

    stats = {"Total": total,
             "Failed_Article": failed_article,
             "Failed_GameGen": failed_gamegen,
             "Syntactic_Error": syntactic_error,
             "Semantic_Update": semantic_update,
             "Outcome_not_in_Equilibrium": notineq,
             "Outcome_in_Equilibirum_but_Degenerate": degenerate,
             "Valid_NonDegenerate_Total": validated,
             "Valid_Single_Equilibrium": single_valid,
             "Valid_Multiple_Equilibria": multieq}
    print(stats)
    return category


