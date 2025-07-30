import textwrap
import google.generativeai as genai
import typing_extensions as typing
from typing import Dict, Any, Tuple, List, Union
import json


def autoformalize_players_actions(agent, description: str) -> dict:
    """
    Autoformalizes a natural language game description into a JSON format based on the provided schema using a Gemini model.

    Args:
        description: A string containing the natural language description of the game.
        agent: A Gemini model object.

    Returns:
        A JSON string representing the formalized players and actions, or None if an error occurs.
    """
    try:
        # Prepare the prompt for the Gemini model.
        prompt = """
        You are an expert game formalization assistant. You are provided with a description of an animal interaction. Your task is to formalize it as a game. We will start by defining the players and their actions. 
        Use the following JSON schema:  

        ```json
        [{"name": str, "actions": list[str]}, {"name": str, "actions": list[str]},...]
        ```

        Adjust the names of the players and their possible actions to fit the provided description. 
        """

        prompt += f"""\nGame Description to formalize:\n{description}\n\n
        Return ONLY the JSON.
        """

        response = agent.get_response(prompt)

        # parse
        response_json = response.split("```json")[-1].split("```")[0]
        response_json = json.loads(response_json)
        return response_json

    except Exception as e:
        print(f"Error during autoformalization: {e}")
        return None


def autoformalize_game(agent, description: str, player: str, json_str: str) -> str:
    """
    Autoformalizes a natural language game description into a JSON format based on the provided schema using a Gemini model.

    Args:
        description: A string containing the natural language description of the game.
        agent: A Gemini model object.

    Returns:
        A JSON string representing the formalized game state, or None if an error occurs.
    """
    try:
        # Prepare the prompt for the Gemini model.
        prompt = "You are an expert game formalization assistant. You are provided with a description of an animal interaction and a JSON string defining the players and possible actions. "
        prompt += f"""\nGame Description to formalize:\n{description}\n\nPlayers and their possible actions:\n{json_str}\n"""
        prompt += f"Your task is to define the utilities of player: {player}"
        prompt += """        
        To define the utilities, use the following JSON schema:  

        ```json
        {action1(str): {response1(str): {"outcome": str, "utility": float}, response2(str): {"outcome": str, utility(float)}, ...}, action2(str): {response1(str): {"outcome": str, "utility": float},...},...]
        ```
        """
        prompt += f"""
        Where "action"s refers to each of the actions from the list of {player} possible actions, "response"s refers to each of the actions of the *other* player, "outcome" is a textual description of the results from the action/respone pair, and "utility" is the numeric value of that outcome for {player}.
        Make sure to include every possible action of {player}, and every possible response of the other player, in the utilities.
        Formalize the utilities for {player} in the precise format and return ONLY the JSON."""

        response = agent.get_response(prompt)

        # parse
        response_json = response.split("```json")[-1].split("```")[0]
        response_json = json.loads(response_json)
        return response_json

    except Exception as e:
        print(f"Error during autoformalization: {e}")
        return None


def autoformalize_expected_outcomes(agent, description, game_space):
    try:
        prompt = """You are an experienced biologist. You are provided with the description of an animal interaction and a JSON string formally defining the players and possible actions of the game.
        Your task is to define the most likely outcome of the game as observed in nature.
        For you answer, use your knowledge, the given description and common sense.
        
        Your answer should be in the following JSON schema:
        
        ```json
        {player(str): action(str), player(str): action(str)}
        ```
        
        Where "player(str)" refers to the name of the player, and "action(str)" refers to the action selected from the set of possible actions of that player.
        Use precise player names and action labels from the JSON string defining the game.
        
        """

        prompt += f"""Interaction of interest: {description}\nFormally defined players and actions: {game_space}\nGame outcome as observed in nature: """

        response = agent.get_response(prompt)

        # parse
        response_json = response.split("```json")[-1].split("```")[0]
        response_json = json.loads(response_json)
        return response_json

    except Exception as e:
        print(f"Error during autoformalization of game outcome: {e}")
        return None


def autoformalize_category(agent, category):
    for i, item in enumerate(category):
        print("processing ", i)
        if item["Article"] != "Error":
            description = (f"Background: {item['Article']}"
                          f"\nInteraction of interest: {item['Description']}")
            game = autoformalize_players_actions(agent, description)
            if game is not None:
                for j, player in enumerate(game):
                    name = player["name"]
                    action_defs = json.dumps(game)
                    utilities = autoformalize_game(agent, description, name, action_defs)
                    if utilities is not None:
                        game[j]["utilities"] = utilities
            category[i]["Game"] = game
    return category


def expected_outcomes_category(agent, category):
    for i, item in enumerate(category):
        print("processing ", i)
        if item["Article"] != "Error" and "Game" in list(item.keys()) and "Error" not in list(item.keys()):
            description = (f"Background: {item['Article']}"
                          f"\nInteraction of interest: {item['Description']}")
            game_string = json.dumps([{x["name"]: x["actions"]} for x in item["Game"]])
            outcome = autoformalize_expected_outcomes(agent, description, game_string)
            if outcome is not None:
                category[i]["Outcome"] = outcome
    return category


def improve_from_feedback(agent, description, game, outcome, feedback):
    try:
        prompt = """You are an expert game formalization assistant. You are provided with the description of an animal interaction, a JSON string formally defining the interaction as a game and the outcome observed in nature.
        The formal game has been analyzed, and its equilibria compared to the outcomes observed in nature. 
        Based on this analysis, you receive professional feedback.
        Your task is to update the game configuration so that it satisfies the problems outlined in the feedback.
        Remember, improving the game you must remain faithful to the description of the interaction, biological plausibility and common sense.

        Your answer should be in exactly the same JSON schema as the original game description, but with updated content.
        """

        prompt += f"""Interaction of interest: {description}\nFormally defined game: {game}\nOutcome observed in nature: {outcome}\nProfessional feedback: {feedback}"""

        prompt += """Remember the correct JSON schema:
        ```json
        [{"name": player1(str), "actions": list[str], "utilities": {action1(str): {response1(str): {"outcome": str, "utility": float},...},...}, {"name": player2(str)... },...]
        ```
        """
        response = agent.get_response(prompt)

        # parse
        response_json = response.split("```json")[-1].split("```")[0]
        response_json = json.loads(response_json)
        return response_json
    except Exception as e:
        print(f"Error during automodel improvement: {e}")
        return None


def update_category(agent, category):
    for i, item in enumerate(category):
        print("processing ", i+1)
        if item["Article"] != "Error" and "Game" in list(item.keys()):
            if "Feedback" in list(item.keys()) and item["Feedback"] != "None":
                description = (f"Background: {item['Article']}"
                              f"\nInteraction of interest: {item['Description']}")
                game = item["Game"]
                outcome = item["Outcome"]
                feedback = item["Feedback"]
                game = improve_from_feedback(agent, description, game, outcome, feedback)
                if game is not None:
                    category[i]["Updated_Game"] = game
    return category
