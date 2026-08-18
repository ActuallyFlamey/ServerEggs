def recursive_find(path: str, dictionary: dict):
    deconstructed_path = path.split("/", 1)

    inner = dictionary[deconstructed_path[0]]

    if len(deconstructed_path) == 1:
        return inner

    return recursive_find(deconstructed_path[1], inner)