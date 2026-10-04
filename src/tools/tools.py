from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str) -> str:
     """Search the web for recent sources matching the query."""
     results = tavily.search(query=query,max_results=5)
     out = []

     for r in results['results']:
          out.append(
               f'Title: {r["title"]}\nURL: {r["url"]}\nSnippet: {r["content"][:300]}\n'
          )

     return "\n------\n".join(out)

def scrape_url(url:str) -> str:
     """
     Scrape and extract clean readable content from a url.
     Uses multiple extraction strategies for better reliability.
     """
     headers = {
          "User-Agent": (
               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/58.0.3029.110 Safari/537.3"
          ),
          "Accept-Language": "en-US,en;q=0.9",
          "Referer": "https://www.google.com/",
     }
     try:
          response = requests.get(url, headers=headers, timeout=10)
          response.raise_for_status()

          html = response.text

          # Strategy 1: Trafilatura
          extracted = trafilatura.extract(html,
                                          include_comments=False,
                                          include_tables=False)
          if extracted and len(extracted.strip()) > 200:
               cleaned = re.sub(r'\s+', ' ', extracted).strip()
               return cleaned[:5000]  # Limit to 5000 characters

          # Strategy 2: Readability
          doc = Document(html)
          readable_html = doc.summary()
          soup = BeautifulSoup(readable_html, 'html.parser')

          for tag in soup([
               'script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'iframe'
          ]):
               tag.decompose()

          text = soup.get_text(separator=' ', strip=True)
          if text and len(text.strip()) > 200:
               cleaned = re.sub(r'\s+', ' ', text).strip()
               return cleaned[:5000]  # Limit to 5000 characters 

          # Strategy 3: Fallback to BeautifulSoup
          soup = BeautifulSoup(html, 'html.parser')
          for tag in soup([
               'script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'iframe'
          ]):
               tag.decompose()
          text = soup.get_text(separator=' ', strip=True)
          cleaned = re.sub(r'\s+', ' ', text).strip()

          if cleaned and len(cleaned.strip()) > 200:
               return cleaned[:5000]  # Limit to 5000 characters

          return "Content could not be extracted or is too short."

     except requests.RequestException as e:
          return f"Error fetching the URL: {e}"
     except Exception as e:
          return f"An error occurred while processing the URL: {e}"
     except requests.exceptions.Timeout:
          return "Request timed out while trying to fetch the URL."   
     except requests.exceptions.HTTPError as e:
          return f"HTTP error occurred: {e}"
     