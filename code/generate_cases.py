import requests
from urllib.parse import quote  # Import for URL encoding
import time
import json


def get_cases(agent, category):
    try:
        # Prepare the prompt for the Gemini model.
        prompt = f"""
        You are an expert biologist. We are looking for interesting cases of animal interaction in the area of {category} dynamics.
        They may be in-species or inter-species interactions.
        Make sure that they are documented real-life cases with clearly observed and recorded behaviors.
        Also, make sure that the cases are interesting, in the sense that they present some non-trivial dilemma for the animals involved.
        Restrict yourself to interaction between two animals only.
        Finally, formulate a search query that will retrieve an article on the subject.
        """
        prompt += """
        Give ten different cases using the following JSON schema:
        
        ```json
        [{"Species": list[str], "Description": str, "Query": str},...]
        ```

        Where the "Species" key refers to a list of the species involved in the interaction, the "Description" key refers to a comprehensive description of the animal interaction and their behavioral outcomes, and "Query" refers to a search query for an article on the subject. 
        Only provide the JSON in the precise schema, without any other text.
        """

        response = agent.get_response(prompt)

        # parse
        response_json = response.split("```json")[-1].split("```")[0]
        response_json = json.loads(response_json)
        return response_json

    except Exception as e:
        print(f"Error during case generation: {e}")
        return None


def wikimedia_search(query: str, language_code: str = 'en') -> str:
    """
    Searches Wikimedia for a given query and returns the full text of the most relevant article.

    This function uses the Wikimedia REST API to perform a search, identifies the
    most relevant article, and retrieves its full text. It handles potential
    errors like search failures and missing articles.

    Args:
        query: The search query string.
        language_code: The language code for the Wikipedia search (e.g., 'en', 'fr', 'de').
                       Defaults to 'en' (English).

    Returns:
        A string containing the full text of the Wikipedia article, or an error message
        if the search fails or no suitable article is found.
    """
    try:
        # 1. Search for the article
        search_query = query  # Use the input query
        number_of_results = 1
        headers = {
            'User-Agent': '***' # Replace with your app name and contact
        }

        base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
        endpoint = '/search/page'
        url = base_url + language_code + endpoint
        parameters = {'q': search_query, 'limit': number_of_results}
        search_response = requests.get(url, headers=headers, params=parameters)
        search_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        search_results = search_response.json()

        if not search_results['pages']:
            return "No results found for your search query."

        # 2. Get the article title (URL-friendly key)
        article_key = search_results['pages'][0]['key']
        article_title = search_results['pages'][0]['title'] # get title
        # 3. Construct the article URL
        article_url = f"https://{language_code}.wikipedia.org/wiki/{quote(article_key)}" # Use quote for url encoding

        # 4. Retrieve the article content using a different API endpoint, and handling potential errors.

        article_response = requests.get(article_url, headers=headers)
        article_response.raise_for_status()  # Raise HTTPError for bad responses
        if article_response.status_code == 200:
            article_text = article_response.text  # Get the full HTML content
            return article_text

        else:
            print("Failed to retrieve article")
            return f"Failed to retrieve the article: HTTP Status Code {article_response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"An error occurred during the API request: {e}"
    except (KeyError, IndexError) as e:
        return f"An error occurred while parsing the API response: {e}.  Check the response structure."
    except Exception as e:
        return f"An error occurred: {e}"


def get_wiki_articles(agent, category):
    """
    :param agent: Gemini model object
    :param category: json list of items with wikipedia queries
    :return: updated json list with the article snippets embedded
    """
    for i, item in enumerate(category):
        print("Querying item ", i)
        for trial in range(3):
            article = wikimedia_search(item["Query"])
            if article.startswith("No results") or article.startswith("An error"):
                print(article)
                error = True
                break
            else:
                error = False
                time.sleep(3)
        if error is False:
            snippet = agent.get_response(f"We are interested in the following phenomenon: {item['Description']}. "
                                         f"\nYou are provided with a wikipedia article in HTML format. "
                                         f"\nExtract the passages from the article that are relevant to the phenomenon of interest. "
                                         f"\nWikipedia article: {article}"
                                         f"\nProvide just the plain text of the relevant passages *without* HTML formatting.")
        elif error is True:
            snippet = "Error"
        category[i]["Article"] = snippet
    return category



