import uuid

keyboard_state = {}

def get_keyboard_state(user_id):
    return keyboard_state.get(user_id)

def set_keyboard_state(user_id, state):
    keyboard_state[user_id] = state

def delete_keyboard_state(user_id):
    keyboard_state.pop(user_id, None)


# A dictionary to map short identifiers to private_key strings
data_map = {}

def generate_uuid_from_pKey(private_key):
    random_uuid = uuid.uuid4()
    short_id = random_uuid.hex
    short_id = short_id[:8]  # To get an 8-character string
    data_map[short_id] = private_key
    return short_id

def get_pKey_from_uuid(short_id):
    return data_map.get(short_id)

