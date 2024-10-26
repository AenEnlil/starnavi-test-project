from typing import List, Dict

from app.database import get_collection_by_name


def paginate_collection(collection_name: str, pipeline: List[Dict], page: int = 1, items_per_page: int = 5):
    pipeline.append({"$group": {"_id": "null", "count": {"$sum": 1}, "results": {"$push": "$$ROOT"}}})
    pipeline.append({"$project": {"count": 1, "rows": {"$slice": ["$results", (page-1) * items_per_page, items_per_page]}}})
    collection = list(get_collection_by_name(collection_name).aggregate(pipeline))
    items = collection[0] if collection else {}
    return {
        "items": items.get('rows', []),
        "total_items_count": items.get('count', 0),
        "page_size": items_per_page,
        "page": page
    }

