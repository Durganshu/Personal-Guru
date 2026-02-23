def get_book_update_prompt(book_title, book_description, current_topics, all_topics, user_query):
    """Generate the prompt for AI-powered book update suggestions."""

    current_topics_text = "\n".join(f"- {name}" for name in current_topics) if current_topics else "- (empty book)"
    all_topics_text = "\n".join(f"- {name}" for name in all_topics)

    return f"""You are a book curator helping to organize a knowledge book.

Current Book: "{book_title}"
Description: {book_description or "No description"}

Current Topics in Book:
{current_topics_text}

All Available Topics:
{all_topics_text}

User Request: "{user_query}"

Based on the user's request, suggest which topics should be added to or removed from the book.

IMPORTANT GUIDELINES:
1. Try to honor the user's request as much as possible
2. If the user asks to add topics, look for the BEST AVAILABLE options even if not perfect
3. Consider relevance to the book's theme, but be flexible
4. Consider logical flow and organization
5. Avoid redundancy with existing topics
6. If truly no suitable topics exist, explain why in the reasoning

Respond in JSON format:
{{
    "add": ["topic1", "topic2"],
    "remove": ["topic3"],
    "reasoning": "Brief explanation of your suggestions"
}}

CRITICAL: Only suggest topics from the "All Available Topics" list above. Use the EXACT topic names.
If no changes are appropriate, return empty arrays for add and remove, but provide helpful reasoning."""



def get_book_description_prompt(book_title, topic_names):
    """Generate the prompt for creating a book description based on topics."""

    topics_text = "\n".join(f"- {name}" for name in topic_names)

    return f"""You are a book curator writing a concise description for a knowledge book.

Book Title: "{book_title}"

Topics in this Book:
{topics_text}

Write a brief, engaging description (2-3 sentences) that:
1. Summarizes what the book covers
2. Highlights the key themes or learning areas
3. Is clear and informative

Respond with ONLY the description text, no JSON, no extra formatting."""


def get_librarian_search_prompt(query, context):
    """Generate the prompt for the LibrarianAgent to search and curate a book."""
    return f"""
        You are an AI Librarian. The user is searching their own library for: "{query}"

        Based on their existing content fragments below, curate a "Book" (a collection of topics).
        Select the most relevant Topic IDs that form a logical learning progression.

        Existing Content:
        {context}

        Return a JSON object with:
        - title: A catchy title for this curated book
        - description: A short description of what this book covers
        - topic_ids: A chronological list of integer Topic IDs to include.
        """


def get_librarian_generate_prompt(query, user_background):
    """Generate the prompt for the LibrarianAgent to generate a new book structure."""
    return f"""
        You are an AI Librarian. The user wants to generate a new book to learn about: "{query}"
        User Background: "{user_background}"

        Design a comprehensive, structured book consisting of 3 to 6 sequential topics (chapters).
        The topics should progressively build knowledge from fundamentals to advanced concepts.

        Return a JSON object with:
        - title: A compelling title for the book
        - description: A short summary of the book's learning objective
        - topics: An ordered list of strings, each being a distinct topic name to generate.
        """
