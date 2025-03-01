import math
from datetime import datetime

import pandas as pd
from rapidfuzz import fuzz, process

from ..utils.pagination import paginate

async def advanced_fuzzy_search_qa(
        df: pd.DataFrame,
        bu_id,
        query: str,
        page,
        total_items,
        title_weight: float = 0.6,
        description_weight: float = 0.4,
        threshold: float = 0.0,
        containment_boost: float = 20.0  # Boost value for containment check
):
    """
    Performs an optimized advanced fuzzy search on the QA DataFrame using vectorized operations.
    The function calculates a composite score based on weighted fuzzy matching on the title and description.
    Additionally, it boosts the score if the query is found as a substring in the title or description.
    """
    if not query:
        return {}

    # Normalize the weights to ensure they sum to 1
    total_weight = title_weight + description_weight
    title_weight = title_weight / total_weight
    description_weight = description_weight / total_weight

    # Normalize the query text (and optionally, you can add more preprocessing like removing punctuation)
    query_norm = query.lower().strip()

    # Prepare FAQ texts: fill missing values and lowercase for consistency
    df['faq_title'] = df['faq_title'].fillna("").astype(str).str.lower().str.strip()
    df['description'] = df['description'].fillna("").astype(str).str.lower().str.strip()

    # Vectorized fuzzy scoring using RapidFuzz's cdist function
    scores_title = process.cdist([query_norm], df['faq_title'].tolist(), scorer=fuzz.token_set_ratio)[0]
    scores_description = process.cdist([query_norm], df['description'].tolist(), scorer=fuzz.token_set_ratio)[0]

    # Containment check: Boost the score if the query is found in the title or description
    containment_boosts = [
        containment_boost if query_norm in title or query_norm in description else 0
        for title, description in zip(df['faq_title'], df['description'])
    ]

    # Calculate composite scores using the normalized weights and adding the containment boost
    composite_scores = [
        title_weight * s_title + description_weight * s_desc + boost
        for s_title, s_desc, boost in zip(scores_title, scores_description, containment_boosts)
    ]

    # Assign scores to the DataFrame
    df['scores_title'] = scores_title
    df['scores_description'] = scores_description
    df['containment_boost'] = containment_boosts
    df['composite_score'] = composite_scores

    # Filter and sort by the composite score (descending)
    search_results = df[df['composite_score'] >= threshold].sort_values(
        by='composite_score', ascending=False
    )

    # Get the top 90 results (3 pages, 30 items each)
    top_results = search_results.head(90)

    # Convert the filtered results to a dictionary
    records = top_results.to_dict(orient='records')

    # Paginate the results, each page contains 30 items
    paginated_results = paginate(items=records, page=page, total_items=total_items)
    total_pages = math.ceil(len(records) / total_items)

    # Prepare the final results
    results = []
    for x in paginated_results:
        results.append({
            '_id': x.get('faq_id', ''),
            'category': x.get('category', ''),
            'title': x.get('faq_title', ''),
            'description': x.get('description', ''),
            'comment': x.get('comment', ''),
            'attachments': x.get('attachments', []),
            'updated_by': x.get('updated_by', ''),
            'updated': x.get('updated', datetime.now()),
            'ai_off': x.get('ai_off', False),
            'scores_title': x.get('scores_title', 0),
            'scores_description': x.get('scores_description', 0),
            'containment_boost': x.get('containment_boost', 0),
            'composite_score': x.get('composite_score', 0)
        })
    
    results = sorted(results, key=lambda x: x['updated'], reverse=True)

    result = {
        "keyspace": bu_id,
        "page": page,
        "total_items": total_items,
        "total_pages": total_pages,
        "total_items_all": len(records),
        "faq_data": results
    }
    return result
