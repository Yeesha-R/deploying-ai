# Atlas Travel Assistant

## Overview

Atlas is an AI-powered travel assistant with a conversational interface built using Gradio. Its goal is to help users plan trips by recommending destinations, providing current weather information, and generating simple travel itineraries.

Atlas has a friendly, practical personality. It responds in a conversational tone while keeping recommendations concise and realistic.

The chatbot maintains conversation history throughout the session, allowing users to ask follow-up questions and continue planning their trips naturally.

---

# Services

## Service 1 – Weather Information (API)

This service uses the **Open-Meteo API** as its backend.

When a user asks about the weather in a city, Atlas:

1. Uses the Open-Meteo Geocoding API to locate the city.
2. Retrieves current weather conditions using the Open-Meteo Weather API.
3. Converts the API response into natural language instead of displaying raw JSON.
4. Provides simple travel advice based on the weather conditions (for example, suggesting an umbrella or warm clothing).

Example:

**User:**

> What is the weather in Lisbon?

**Atlas:**

> Atlas weather update for Lisbon: It is currently 24°C with partly cloudy skies. A light jacket may be useful for the evening.

---

## Service 2 – Semantic Destination Search

Atlas recommends travel destinations using semantic search with **ChromaDB**.

A custom dataset (`destinations.csv`) contains information about destinations, including:

* destination
* country
* description
* activities
* best season
* budget level
* travel style

The destination descriptions are converted into vector embeddings and stored in a persistent ChromaDB collection.

When the user asks questions such as:

> I want mountains, lakes, and hiking.

Atlas performs a semantic search and recommends the most relevant destinations instead of relying on keyword matching alone.

The ChromaDB database uses file persistence, allowing the embeddings to be generated once and reused in future sessions.

---

## Service 3 – Trip Planner (Function Calling)

Atlas includes a trip-planning service implemented using **function calling**.

When the user requests an itinerary, the language model extracts structured information such as:

* destination
* number of travel days
* budget
* traveller interests

These arguments are passed to a Python function that generates a structured itinerary.

The itinerary is then formatted into a natural day-by-day travel plan.

Example:

> Plan a 3-day budget trip to Kyoto focused on history.

Atlas produces a multi-day itinerary rather than asking the language model to invent one directly.

---

# Chat Interface

The application uses **Gradio ChatInterface** to provide a conversational interface.

Conversation history is preserved throughout the session, allowing Atlas to remember previous messages and answer follow-up questions.

To prevent the context from growing indefinitely, only the most recent conversation history is sent to the language model.

---

# Personality

Atlas is designed as a helpful travel guide.

Its personality is:

* friendly
* practical
* encouraging
* concise
* realistic

Atlas avoids making unrealistic promises and encourages users to verify important travel information when necessary.

---

# Memory Management

The chatbot maintains short-term conversational memory by preserving previous messages during the current chat session.

To reduce context size, older messages are discarded after a configurable number of exchanges. This provides a simple form of short-term memory management while preventing the prompt from becoming excessively large.

---

# Guardrails

Atlas includes several guardrails.

### Prompt Protection

The chatbot refuses attempts to:

* reveal the system prompt
* reveal hidden instructions
* modify the system prompt
* ignore previous instructions

### Restricted Topics

The chatbot refuses to answer questions related to:

* cats or dogs
* horoscopes or zodiac signs
* Taylor Swift

Instead, Atlas redirects the conversation back to travel-related topics.

---

# Embedding Process

The destination dataset is stored as a CSV file.

A preprocessing script (`build_embeddings.py`) performs the following steps:

1. Reads the destination dataset using pandas.
2. Combines destination information into a searchable document.
3. Generates embeddings using ChromaDB's default embedding function.
4. Stores the embeddings in a persistent ChromaDB database located in the `chroma_db` directory.

The embedding script only needs to be run when the dataset changes.

---

# Project Structure

```text
assignment_chat/
├── app.py
├── build_embeddings.py
├── guardrails.py
├── readme.md
├── chroma_db/
├── data/
│   └── destinations.csv
└── services/
    ├── destination_search.py
    ├── itinerary_service.py
    └── weather_service.py
```

---

# Technologies Used

* Python
* Gradio
* OpenAI API
* ChromaDB
* pandas
* Open-Meteo API

---

# Running the Project

1. Generate the embeddings:

```bash
python build_embeddings.py
```

2. Set your OpenAI API key.

Example (PowerShell):

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
```

3. Launch the application:

```bash
python app.py
```

4. Open the local Gradio URL in your browser.

---

# Design Decisions

Several design decisions were made to keep the project simple while satisfying the assignment requirements:

* Open-Meteo was selected because it is free and does not require an API key.
* ChromaDB was chosen for semantic search because it supports persistent local storage and was required by the assignment.
* Function calling was used for itinerary generation to demonstrate structured tool use instead of relying solely on natural language generation.
* A lightweight keyword router determines which service should handle each user request before invoking the appropriate functionality.
* Simple guardrails were implemented to prevent prompt injection attempts and enforce the assignment's restricted-topic requirements.
