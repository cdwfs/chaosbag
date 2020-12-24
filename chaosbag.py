#!/usr/bin/env python3
"""Commands:
  help                        Print this message
  print                       Print chaos bag contents and relevant odds
  add [<token> ...]           Add the listed token(s) to the chaos bag
  remove [<token> ...]        Remove the listed token(s) from the chaos bag
  set <token> <modifier>      Sets the modifier value for the provided token
  reset                       Reset the bag to its default state (empty)
  load                        Load the bag state from a backup file (WIP)
  exit                        Quits
  
Token name | default value | notes
----------------------------------
    ES     |      +1       | elder sign (star)
    SK     |       0       | skull
    TA     |       0       | tablet
    CU     |       0       | cultist
    EL     |       0       | elder thing
    WI     |      -9       | MISTER WIGGLES (tentacles (auto-fail))
    +1     |      +1       |
     0     |       0       |
    -1     |      -1       |
    -2     |      -2       |
    -3     |      -3       |
    -4     |      -4       |
    -5     |      -5       |
    -6     |      -6       |
    -7     |      -7       |
    -8     |      -8       |
"""
import pathlib
import pickle
import re
import sys

BACKUP_FILENAME = pathlib.Path.home() / ".chaosbag"
ADD_RE = re.compile(r"^add\s+(?P<tokens>.+)$")
REMOVE_RE = re.compile(r"^add\s+(?P<tokens>.+)$")
SET_RE = re.compile(r"^set\s+(?P<token>ES|SK|TA|CU|EL|WI)\s+(?P<value>[+-]?\d+)$")
VALID_TOKENS = ["ES", "SK", "TA", "CU", "EL", "WI", "+1", "+0", "-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8"]
DEFAULT_TOKEN_VALUES = {
  "ES":+1,
  "SK":0,
  "TA":0,
  "CU":0,
  "EL":0,
  "WI":-9,
  "+1":+1,
  "+0":+0,
  "-1":-1,
  "-2":-2,
  "-3":-3,
  "-4":-4,
  "-5":-5,
  "-6":-6,
  "-7":-7,
  "-8":-8,
}

def print_bag(bag, token_values):
  token_count = len(bag)
  # General per token odds
  print("Modifiers:")
  tokens_for_value = {}
  for token in bag:
    v = token_values[token]
    if v not in tokens_for_value:
      tokens_for_value[v] = []
    tokens_for_value[v].append(token)
  sorted_values = list(tokens_for_value.keys())
  sorted_values.sort()
  sorted_values.reverse()
  above_count = 0
  for v in sorted_values:
    bucket_count = len(tokens_for_value[v])
    equal_percent = 100.0 * float(bucket_count) / token_count
    above_percent = 100.0 * float(bucket_count+above_count) / token_count
    below_percent = 100.0 * float(token_count-above_count) / token_count
    print("%3d: ==%3.0f%% | >=%3.0f%% | <=%3.0f%% | %s" % (v, equal_percent, above_percent, below_percent, ", ".join(tokens_for_value[v])))
    above_count += bucket_count
  # Odds of SK,CU,TA,EL for Ritual Candles, etc.
  bad_count = bag.count("SK") + bag.count("CU") + bag.count("CU") + bag.count("TA") + bag.count("EL")
  bad_percent = 100.0 * float(bad_count) / token_count
  print("SK/CU/TA/EL:    %3.0f%%" % bad_percent)
  # Odds of SK,CU,TA,EL,WI for Mists of R'lyeh etc.
  really_bad_count = bad_count + bag.count("WI")
  really_bad_percent = 100.0 * float(really_bad_count) / token_count
  print("SK/CU/TA/EL/WI: %3.0f%%" % really_bad_percent)
  # Odds of ES, +1, 0 for Clairvoyance, Azure Flame, etc.
  good_count = bag.count("ES") + bag.count("+1") + bag.count("+0")
  good_percent = 100.0 * float(good_count) / token_count
  print("ES/+1/+0:       %3.0f%%" % good_percent)
  # Even/odd/symbol odds for Prescient
  even_count = bag.count("+0") + bag.count("-2") + bag.count("-4") + bag.count("-6") + bag.count("-8")
  odd_count = bag.count("+1") + bag.count("-1") + bag.count("-3") + bag.count("-5") + bag.count("-7")
  symbol_count = token_count - (even_count + odd_count)
  even_percent = 100.0 * float(even_count) / token_count
  odd_percent = 100.0 * float(odd_count) / token_count
  symbol_percent = 100.0 * float(symbol_count) / token_count
  print("Even: %3.0f%% | Odd: %3.0f%% | Symbol: %3.0f%%" % (even_percent, odd_percent, symbol_percent))
  # TODO:
  # - something something Olive McBride

def normalize_token(token):
  if token in ["0"]:
    return "+0"
  elif token in ["1"]:
    return "+1"
  # TODO: additional aliases
  return token

def add_tokens_to_bag(bag, tokens):
  for token in tokens:
    token = normalize_token(token)
    if token in VALID_TOKENS:
      bag.append(token)
    else:
      print("ERROR: Unrecognized token '%s' must be one of [%s]" % (token, ", ".join(VALID_TOKENS)))
  return True

def remove_tokens_from_bag(bag, tokens):
  for token in tokens:
    token = normalize_token(token)
    if token in VALID_TOKENS:
      try:
        bag.remove(token)
      except ValueError:
        print("ERROR: skipping '%s' because there's none of them in the bag" % token)
    else:
      print("ERROR: Unrecognized token '%s' must be one of [%s]" % (token, ", ".join(VALID_TOKENS)))
  return True

def save_bag_to_file(bag, token_values):
    pickle.dump((bag,token_values), open(BACKUP_FILENAME, "wb"))

# returns (bag, token_values) tuple
def load_bag_from_file():
    bag, token_values = pickle.load(open(BACKUP_FILENAME, "rb"))
    return (bag, token_values)

if __name__ == "__main__":
  token_values = DEFAULT_TOKEN_VALUES.copy()
  bag = []
  while True:
    # Read a new command & see what commands it matches
    cmd = input("> ")
    add_match = ADD_RE.search(cmd)
    remove_match = REMOVE_RE.search(cmd)
    set_match = SET_RE.search(cmd)
    if cmd in ["help", "?"]:
      print(__doc__)
      continue
    elif cmd in ["quit", "exit"]:
      sys.exit(0)
    elif cmd in ["print"]:
      print_bag(bag, token_values)
    elif cmd in ["reset", "clear"]:
      bag = []
      token_values = DEFAULT_TOKEN_VALUES.copy()
      continue
    elif cmd == "load":
      bag, tokens = load_bag_from_file()
      print_bag(bag, token_values)
    elif add_match is not None:
      if add_tokens_to_bag(bag, add_match.group('tokens').split()):
        save_bag_to_file(bag, token_values)
        print_bag(bag, token_values)
    elif remove_match is not None:
      if remove_tokens_from_bag(bag, remove_match.group('tokens').split()):
        save_bag_to_file(bag, token_values)
        print_bag(bag, token_values)
    elif set_match is not None:
      token = set_match.group('token')
      value = int(set_match.group('value'))
      token = normalize_token(token)
      token_values[token] = value
      save_bag_to_file(bag, token_values)
      print_bag(bag, token_values)
    else:
      print("Unrecognized command. Usage:")
      print(__doc__)
