from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import search

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/search_books", methods=["POST"])
def search_books():
    search_query = request.json.get("search_query", "")
    search_scopes = request.json.get("search_scopes", "")
    s = search.SearchBooks()
    code, message = s.get_books(search_query=search_query, search_scopes=search_scopes)
    if code == 200:
        return jsonify({"code": code, "books": message['titles'], "total_results": message['num']}), 200
    else:
        return jsonify({"code": code, "message": message}), code


@bp_search.route("/search_stores", methods=["POST"])
def search_stores():
    search_query = request.json.get("search_query", "")
    search_scopes = request.json.get("search_scopes", "")
    store_name = request.json.get("store_name", "")
    s = search.SearchBooks()
    code, message = s.get_stores(store_name=store_name,search_query=search_query, search_scopes=search_scopes)
    if code == 200:
        return jsonify({"code": code, "books": message['titles'], "total_results": message['num']}), 200
    else:
        return jsonify({"code": code, "message": message}), code
