import pandas as pd
from datetime import datetime

# Create a sample DataFrame for testing
data = {
    "faq_id": [1, 2, 3, 4, 5],
    "category": ["General", "Billing", "Technical", "Account", "General"],
    "faq_title": [
        "How to reset my password?",
        "How to update billing information?",
        "Troubleshooting login issues",
        "How to delete my account?",
        "What is the refund policy?"
    ],
    "description": [
        "Follow these steps to reset your password.",
        "You can update your billing information in the account settings.",
        "If you are unable to log in, try resetting your password or contact support.",
        "To delete your account, go to settings and follow the instructions.",
        "Our refund policy allows refunds within 30 days of purchase."
    ],
    "comment": ["", "", "", "", ""],
    "attachments": [[], [], [], [], []],
    "updated_by": ["admin", "admin", "admin", "admin", "admin"],
    "updated": [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3),
        datetime(2023, 1, 4),
        datetime(2023, 1, 5)
    ],
    "ai_off": [False, False, False, False, False]
}

# Convert the dictionary to a pandas DataFrame
df = pd.DataFrame(data)

import asyncio

# Define a mock paginate function (since it's imported in the code)
def paginate(items, page, total_items):
    start = (page - 1) * total_items
    end = start + total_items
    return items[start:end]

# Define the query and parameters
query = "reset password"
page = 1
total_items = 2  # Number of items per page
title_weight = 0.6
description_weight = 0.4
threshold = 50.0  # Minimum composite score to include in results
containment_boost = 20.0

# Call the function
result = asyncio.run(
    advanced_fuzzy_search_qa(
        df=df,
        bu_id="test_bu",
        query=query,
        page=page,
        total_items=total_items,
        title_weight=title_weight,
        description_weight=description_weight,
        threshold=threshold,
        containment_boost=containment_boost
    )
)

# Print the result
import pprint
pprint.pprint(result)

