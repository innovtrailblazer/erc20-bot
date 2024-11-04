from sqlite3 import connect

conn = connect('test4.db')
cur = conn.cursor()

def init():
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, pKey TEXT, pKeys TEXT, contracts TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS contract_details (id TEXT PRIMARY KEY, chain TEXT, token_name TEXT, token_symbol TEXT, deployer_key TEXT, verified BOOLEAN DEFAULT FALSE)')
    cur.execute('CREATE TABLE IF NOT EXISTS whitelist (id TEXT PRIMARY KEY)')
    conn.commit()

def add_user(id, pKey):
    cur.execute('INSERT INTO users (id, pKey, pKeys) VALUES (?, ?, ?)', (id, pKey, pKey))
    conn.commit()

def add_pKey(id, pKey):
    cur.execute('SELECT * FROM users WHERE id = ?', (id,))
    existing_user = cur.fetchone()
    print(f"get existing user: {existing_user}")

    if existing_user:
        # User exists, update pKeys
        pKeys: str = existing_user[2] if existing_user[2] is not None else ''
        pKeys += ',' + pKey
        cur.execute('UPDATE users SET pKeys = ? WHERE id = ?', (pKeys, id))
        conn.commit()
    else:
        add_user(id, pKey)

def set_pKey(id, pKey):
    cur.execute('UPDATE users SET pKey = ? WHERE id = ?', (pKey, id))
    conn.commit()

def delete_pKey(id, pKey):
    cur.execute('SELECT * FROM users WHERE id = ?', (id,))
    existing_user = cur.fetchone()
    print(f"get existing user: {existing_user}")

    if existing_user:
        # User exists, update pKeys
        pKeys: str = existing_user[2] if existing_user[2] is not None else ''
        pKeysArray = pKeys.split(',')
        if pKey in pKeysArray:
            pKeysArray.remove(pKey)
        pKeys = ','.join(pKeysArray)
        cur.execute('UPDATE users SET pKeys = ? WHERE id = ?', (pKeys, id))
        conn.commit()

def get_user(id):
    cur.execute('SELECT * FROM users WHERE id = ?', (id,))
    return cur.fetchone()

def add_contract(id, contract):
    cur.execute('SELECT * FROM users WHERE id = ?', (id,))
    existing_user = cur.fetchone()
    print(f"get existing user: {existing_user}")

    if existing_user:
        # User exists, update contracts
        contracts: str = existing_user[3] if existing_user[3] is not None else ''
        contracts += ',' + contract
        cur.execute('UPDATE users SET contracts = ? WHERE id = ?', (contracts, id))
        conn.commit()


def get_contracts(id):
    cur.execute('SELECT contracts FROM users WHERE id = ?', (id,))
    return cur.fetchone()[0]

def verify_contract(id):
    cur.execute('UPDATE contract_details SET verified = ? WHERE id = ?', (True, id))
    conn.commit()

def get_verification_status(id):
    cur.execute('SELECT verified FROM contract_details WHERE id = ?', (id,))
    return cur.fetchone()[0]

def get_private_key(id):
    cur.execute('SELECT pKey FROM users WHERE id = ?', (id,))
    return cur.fetchone()[0]

def add_contract_details(id, details, pKey):
    cur.execute('INSERT INTO contract_details (id, chain, token_name, token_symbol, deployer_key) VALUES (?, ?, ?, ?, ?)', (id, details['chain'], details['token_name'], details['token_symbol'], pKey))
    conn.commit()

def get_deployer_contracts(pKey):
    cur.execute('SELECT * FROM contract_details WHERE deployer_key = ?', (pKey,))
    return cur.fetchall()

def get_contract_details(id):
    cur.execute('SELECT * FROM contract_details WHERE id = ?', (id,))
    return cur.fetchone()

def add_whitelist(id):
    cur.execute('INSERT INTO whitelist (id) VALUES (?)', (id,))
    conn.commit()

def get_whitelist(id):
    cur.execute('SELECT * FROM whitelist WHERE id = ?', (id,))
    return cur.fetchone()

def remove_whitelist(id):
    cur.execute('DELETE FROM whitelist WHERE id = ?', (id,))
    conn.commit()

def get_all_whitelist():
    cur.execute('SELECT * FROM whitelist')
    return cur.fetchall()

# print(get_all_whitelist())

# conn.close()