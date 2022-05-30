import json
from venv import create
import networkx as nx
from collections import Counter

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
                print(match["home_team"]["home_team_name"],
                      "-", match["away_team"]["away_team_name"])
        # print(len(data))


def get_passes(match_id, team_name):
    passes = []
    with open(f'./data/events/{match_id}.json', encoding='utf-8') as f:
        events = json.load(f)
        for event in events:
            if event["type"]["id"] == 30 and event["team"]["name"] == team_name:
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


def create_graphs(match_id, team_name):
    passes = get_passes(match_id, team_name)
    # Get missed and successful passes as edges between zones
    zones_missed, zones_succ = get_passing_zones(passes)

    # Count passes between zones
    edges_missed = Counter(zones_missed)
    edges_succ = Counter(zones_succ)

    # List of all zones
    nodes = list(range(1, 9))

    G_missed = nx.DiGraph(name="Missed passes")
    G_missed.add_nodes_from(nodes)
    G_missed.add_edges_from([(x, y, {'weight': v})
                            for (x, y), v in edges_missed.items()])

    G_succ = nx.DiGraph(name="Missed successful")
    G_succ.add_nodes_from(nodes)
    G_succ.add_edges_from([(x, y, {'weight': v})
                          for (x, y), v in edges_succ.items()])

    return G_missed, G_succ


def create_player_zone_graph(match_id, team_name):

    passes = get_passes(match_id, team_name)
    print(f"Total passes: {len(passes)}")
    nodes_succ = set()
    edges_succ = []
    nodes_fail = set()
    edges_fail = []

    for pess in passes:
        start = pess["location"]
        end = pess["pass"]["end_location"]
        if "outcome" in pess["pass"]:
            zone_start = get_zone(start)
            zone_end = get_zone(end)
            player_passer = pess['player']['id']
            player_passer_name = pess['player']['name']
            player_recipient_name = ''
            player_recipient = -1

            node_start = (zone_start, player_passer, player_passer_name)
            node_end = (zone_end, player_recipient, player_recipient_name)
            edge = (node_start, node_end)

            nodes_fail.add(node_start)
            nodes_fail.add(node_end)
            edges_fail.append(edge)

        else:
            zone_start = get_zone(start)
            zone_end = get_zone(end)
            player_passer = pess['player']['id']
            player_passer_name = pess['player']['name']
            player_recipient = pess["pass"]["recipient"]["id"]
            player_recipient_name = pess["pass"]["recipient"]["name"]

            node_start = (zone_start, player_passer, player_passer_name)
            node_end = (zone_end, player_recipient, player_recipient_name)
            edge = (node_start, node_end)

            nodes_succ.add(node_start)
            nodes_succ.add(node_end)
            edges_succ.append(edge)

    print(len(edges_succ) + len(edges_fail))
    nodes_dict = {
        'fail': {},
        'succ': {}
    }

    G_missed = nx.DiGraph(name="Missed passes")
    G_succ = nx.DiGraph(name="Successful passes")

    for i, label in enumerate(nodes_fail):
        nodes_dict['fail'][label] = i
        G_missed.add_node(i, zone=label[0], player=label[1], player_name=label[2])

    for i, label in enumerate(nodes_succ):
        nodes_dict['succ'][label] = i
        G_succ.add_node(i, zone=label[0], player=label[1], player_name=label[2])

    count_edges_fail = Counter(edges_fail)
    for edge_label, edge_weight in count_edges_fail.items():
        start, end = edge_label
        edge_start = nodes_dict["fail"][start]
        edge_end = nodes_dict["fail"][end]
        G_missed.add_edge(edge_start, edge_end, weight=edge_weight)

    count_edges_succ = Counter(edges_succ)
    for edge_label, edge_weight in count_edges_succ.items():
        start, end = edge_label
        edge_start = nodes_dict["succ"][start]
        edge_end = nodes_dict["succ"][end]
        G_succ.add_edge(edge_start, edge_end, weight=edge_weight)

    return G_missed, G_succ


# Barcelona-villarreal: 3773593
# Barcelona-Real: 3773585

# get_match_data(11, 90, 3773593)
# get_match_data(11, 90, 3773585)

# get_passes(15946)
create_player_zone_graph(3773593, "Barcelona")


# create_graphs(3773585)
