def search_inventory(similarity_list):
    if not similarity_list:
        return []
    return sorted(similarity_list, key=lambda x: x[1], reverse=True)
