import requests
import sys
import os
from .config import Config


def serper_search(query):
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        "X-API-KEY": "",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        results = response.json().get('organic', [])
        return results[:10]  # Return only the first 10 results
    else:
        print('Error:400')
        return ['Error:400']


def process_search_results(results):
    print(results)
    processed_results = []
    for i, item in enumerate(results, 1):
        processed_results.append({
            'id': i,
            'title': item.get('title', ''),
            'snippet': item.get('snippet', ''),
            'link': item.get('link', '')
        })
    return processed_results


if __name__ == '__main__':
    # Simple test case
    test_query = "最新的金融科技趋势"
    print(f"Searching for: {test_query}")

    results = serper_search(test_query)
    processed_results = process_search_results(results)

    print(f"\nFound {len(processed_results)} results:")
    for result in processed_results:
        print(f"\n{result['id']}. {result['title']}")
        # Print first 100 characters of snippet
        print(f"{result['snippet'][:100]}...")

    print("\nTest completed.")

    # Now let's pass these results to the chat function
    from chat import chat_with_gpt, generate_context

    context = generate_context(processed_results)
    chat_query = "总结一下这些金融科技趋势"
    chat_response = chat_with_gpt(chat_query, context)

    print("\nChat Query:")
    print(chat_query)
    print("\nChat Response:")
    print(chat_response)
