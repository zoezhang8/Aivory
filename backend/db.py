def search_inventory(similarity_list):
    if not similarity_list:
        return "No matches found"
    similarity_list.sort(key=lambda x: x[1], reverse=True)
    best_match = similarity_list[0]
    return f"Matched item: {os.path.basename(best_match[0])} (Similarity Score: {best_match[1]:.2f})"
