from src.agents.agents import build_search_agent, build_scrape_agent, writer_chain, critic_chain    

def research_pipeline(topic: str) -> dict:
    state = {}
    # Step 1: Research the topic using the search agent

    print("\n"+"="*50)
    print("Step 1 - Researching the topic...")
    print("="*50)

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages":[("user",f"Find recent, reliable and detailed information about the topic: {topic}. Provide a summary of the key points and relevant sources.")]
    })
    state['search_results'] = search_results['messages'][-1].content
    print("\n search results: ", state['search_results'])

    # Step 2: Scrape the relevant sources using the scrape agent
    print("\n"+"="*50)
    print("Step 2 - Scraping the relevant sources...")
    print("="*50)

    scrape_agent = build_scrape_agent()
    scrape_results = scrape_agent.invoke({
        "messages":[("user",
                     f"Based on the following search results about '{topic}'"
                     f"pick the most relevant url and scrape it for deeper content.\n\n"
                     f"Search Results: {state['search_results'][:800]}"
                    )]
    })

    state['scrape_results'] = scrape_results['messages'][-1].content
    print("\n scrape results: ", state['scrape_results'])

    # Step 3: Writer chain
    print("\n"+"="*50)
    print("Step 3 - Writing the article...")
    print("="*50)

    research_combined = (
        f"Search Results: {state['search_results']}\n\n"
        f"Scrape Results: {state['scrape_results']}"
    )

    state['report'] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n report: ", state['report'])


    # Step 4: Critic chain
    print("\n"+"="*50)
    print("Step 4 - Critiquing the article...")
    print("="*50)

    state['critique'] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n critique: ", state['critique'])

    return state
