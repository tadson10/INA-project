import json
from venv import create


zones = {
  1: [(0, 18), (18, 62)],
  2: [(18, 18), (60, 62)],
  3: [(60, 18), (102, 62)],
  4: [(102, 18), (120, 62)],
  5: [(0, 0), (60, 18)],
  6: [(60, 0), (120, 18)],
  7: [(0, 62), (60, 80)],
  8: [(60, 62), (120, 80)]
}

def get_match_data(competition, season, match_id):
  with open(f'./data/matches/{competition}/{season}.json', encoding='utf-8') as f:
    data = json.load(f)
    for match in data:
      if match["match_id"] == match_id:
        print(match["home_team"]["home_team_name"], "-", match["away_team"]["away_team_name"])
    # print(len(data))

def get_passes(match_id):
  passes = []
  with open(f'./data/events/{match_id}.json', encoding='utf-8') as f:
    events = json.load(f)
    for event in events:
      if event["type"]["id"] == 30:
        passes.append(event)
  return passes

def get_passing_zones(passes):
  zones_missed = []
  zones_succ = []
  print(len(passes))
  for pess in passes:
    start = pess["location"]
    end = pess["pass"]["end_location"]
    if "outcome" in pess["pass"]:
      outcome = pess["pass"]["outcome"]
      # print(outcome)
      zone_start = get_zone(start)
      zone_end = get_zone(end)
      zones_missed.append((zone_start, zone_end))
    else:
      # Successful pass
      zone_start = get_zone(start)
      zone_end = get_zone(end)
      # print((zone_start, zone_end))
      zones_succ.append((zone_start, zone_end))
  return zones_missed, zones_succ

def get_zone(point):
  for key in zones:
    zone = zones[key]
    # print(point, zone)
    if (point[0] >= zone[0][0] and point[0] <= zone[1][0] and point[1] >= zone[0][1] and point[1] <= zone[1][1]):
      return key
  print("Error, no zone! - ", point)
  return False

def create_graphs(match_id):
  passes = get_passes(match_id)
  # tuki dobimo edge za uspešne pa zgrešene podaje
  zones_missed, zones_succ = get_passing_zones(passes)
  print(zones_missed)

# get_passes(15946)
create_graphs(15946)