import json
from flask import request

# Optional paging for every list the API returns.
#
#   GET /api/get/student                      -> every student (as before)
#   GET /api/get/student?page=2&per_page=50   -> students 51 to 100
#
# A paged answer looks like:
#   {"data": [...], "page": 2, "per_page": 50, "total": 230, "pages": 5}

MAX_PER_PAGE = 200


def paginate_list_response(response):
    """Runs after each request. Pages the list in a JSON answer when ?page= was sent."""
    page_text = request.args.get("page")
    if not page_text or response.status_code != 200 or not response.is_json:
        return response

    try:
        page = int(page_text)
        per_page = int(request.args.get("per_page", "50"))
    except ValueError:
        return response

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 50
    if per_page > MAX_PER_PAGE:
        per_page = MAX_PER_PAGE

    data = response.get_json(silent=True)

    # Find the list: either the whole answer, or inside "data" / "assignments"
    rows = None
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        for key in ["data", "assignments"]:
            if isinstance(data.get(key), list):
                rows = data[key]
    if rows is None:
        return response

    total = len(rows)
    start = (page - 1) * per_page
    end = start + per_page

    pages = total // per_page
    if total % per_page != 0:
        pages = pages + 1

    paged = {
        "data": rows[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages
    }
    response.set_data(json.dumps(paged, default=str))
    return response
