import random
from dataclasses import dataclass

"""There is no main class here to keep state information (like the db connection)"""

"""
DB SCHEMA

The text of every message is checked against the INPUTS table. If any matches are found, 
the trigger_id is dug up. The popularity field is incremented, and an appropriate output
is chosen and sent.

======= TABLE OUTPUTS ========
PRIMARY KEY INT output_id - internal use for this entry
INT trigger_id - which trigger this corresponds to
TEXT string - what text to output
INT weight - an int weight to attach to this output. Allows some outputs to be sent more often than others.

======= TABLE INPUTS =========
PRIMARY KEY INT input_id - internal use for this entry
INT trigger_id - which trigger this corresponds to
STRING text - what text input
BOOL regex DEFAULT FALSE - whether to treat the trigger strings as regex
BOOL case_sensitive DEFAULT FALSE - whether to only match same-case with the trigger strings (if not regex)

======= TABLE MAIN =========
PRIMARY KEY INT trigger_id - internal use for this entry
STRING name - human readable reference name for this entry
INT popularity DEFAULT 0 - times this has been triggered




CREATE TABLE IF NOT EXISTS outputs 
    (output_id INTEGER PRIMARY KEY, 
    trigger_id INTEGER,             # which trigger this corresponds to
    string TEXT,                    # what text to output (usually a link/url)
    weight INTEGER DEFAULT 1)       # weight to attach to this output. Allows some outputs to be sent more often than others.

CREATE TABLE IF NOT EXISTS inputs 
    (input_id INTEGER PRIMARY KEY, 
    trigger_id INTEGER,             # which trigger this corresponds to
    string TEXT,                    # what string to match against to run the trigger
    regex INTEGER DEFAULT 0,          # bool, whether to treat the trigger strings as regex
    case_sensitive INTEGER DEFAULT 0) # bool, whether to only match same-case with the trigger strings (if not regex)

CREATE TABLE IF NOT EXISTS main 
    (trigger_id INTEGER PRIMARY KEY, 
    name TEXT,                        # human readable reference name for this entry
    popularity INTEGER DEFAULT 0)     # times this has been triggered


python      sqlite type
-------------------------
int         INTEGER
str         TEXT
None        NULL
float       REAL
bytes       BLOB


"""


def get_trigger_outputs_for_msg(db, msg: str):
    to_return = []
    for trigger_id in get_triggers_id_for_msg(db, msg):
        # outputs
        outputs = [e for e in db.execute("SELECT string, weight FROM outputs WHERE trigger_id = ?", (trigger_id,))]
        nested_options = [[option[0]] * option[1] for option in
                          outputs]  # just an intermediary, to get the weights right
        options = [item for sublist in nested_options for item in sublist]
        to_return.append(random.choice(options))

        # the most important bit
        db.execute("UPDATE main SET popularity = popularity + 1 WHERE trigger_id = ?", (trigger_id,))
        db.commit()
    return to_return


def get_triggers_id_for_msg(db, msg: str):
    matches = []
    for i in db.execute("SELECT * FROM inputs"):
        hmm = DBEntryInputs(*i)
        if hmm.regex:
            pass  # todo: actually write regex matching
        elif hmm.case_sensitive:
            if hmm.string in msg:
                matches.append(hmm.trigger_id)
        else:  # case insensitive match
            if hmm.string.lower() in msg.lower():
                matches.append(hmm.trigger_id)
    return matches


def add_to_db(db, name: str, trigger: str, url: str):
    db.execute("INSERT INTO MAIN(name) VALUES (?)", (name,))
    trigger_id = db.execute("SELECT trigger_id FROM main WHERE name = ?", (name,)).fetchone()[0]
    db.execute("INSERT INTO OUTPUTS(trigger_id, string) VALUES (?, ?)", (trigger_id, url))
    db.execute("INSERT INTO INPUTS(trigger_id, string) VALUES (?, ?)", (trigger_id, trigger))
    db.commit()


'''Classes for extracting data from database'''


@dataclass()
class DBEntryOutputs:
    output_id: int
    trigger_id: int
    string: str
    weight: int


@dataclass()
class DBEntryInputs:
    input_id: int
    trigger_id: int
    string: str
    regex: bool
    case_sensitive: bool


@dataclass()
class DBEntryMain:
    trigger_id: int
    name: str
    popularity: int
    outputs: list[DBEntryOutputs]
    inputs: list[DBEntryInputs]


def fetch_from_db(db, name: str):
    res = db.execute("select * from main where name = ?", (name,)).fetchone()
    if not res:
        return None
    trigger_id = res[0]
    outputs = []
    inputs = []
    for output in db.execute("select * from outputs where trigger_id = ?", (trigger_id,)):
        outputs.append(DBEntryOutputs(*output))
    for input in db.execute("select * from inputs where trigger_id = ?", (trigger_id,)):
        inputs.append(DBEntryInputs(input[0], input[1], input[2], bool(input[3]), bool(input[4])))
    return DBEntryMain(trigger_id, name, res[2], outputs, inputs)
