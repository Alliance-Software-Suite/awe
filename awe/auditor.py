import json
import typing

import prettytable as pt
import requests
import tabulate

from cfg import Conf
from graphqlclient import GraphQLClient


class Nation:
    def __init__(self):
        self.mmr_violations = [0, 0, 0, 0]
        self.city_count = 0


def request(client, query):
    for nation in json.loads(
        client.execute(
            f"query{{nations({query},first:500)"
            f"{{data{{id,nation_name,num_cities,cities{{barracks,factory,hangar,drydock}}}}}}}}"
        )
    )["data"]["nations"]["data"]:
        yield nation


def do_audit(cfg: Conf) -> None:
    client = GraphQLClient(
        "https://api.politicsandwar.com/graphql?api_key=" + cfg["key"]
    )

    if len(cfg["nations"]) != 0 and len(cfg["alliances"]) != 0:
        raise RuntimeError("-n/--nation and -a/--alliance are mutually exclusive.")
    if len(cfg["nations"]) != 0:
        query = f"id:{cfg['nations']}"
    elif len(cfg["alliances"]) != 0:
        query = f"alliance_id:{cfg['alliances']}"
    else:
        raise RuntimeError("One of -n/--nation or -a/--alliance must be included.")

    for nation in request(client, query):
        mmr = tuple(int(unit) for unit in cfg["mmr"])

        total_mil = [0] * 4
        max_mil = [0] * 4
        min_mil = [5] * 4
        for city in nation["cities"]:
            mil = (city["barracks"], city["factory"], city["hangar"], city["drydock"])
            for i, m in enumerate(mil):
                total_mil[i] += m
                if max_mil[i] < m:
                    max_mil[i] = m
                if min_mil[i] > m:
                    min_mil[i] = m
        avg_mil = [round(m / nation["num_cities"]) for m in total_mil]
        m2s = lambda m: "".join([str(v) for v in m])
        print(
            tabulate.tabulate(
                [[m2s(avg_mil), m2s(min_mil), m2s(max_mil)]],
                headers=["Average", "Minimum", "Maximum"],
                tablefmt="grid",
                stralign="center",
                numalign="center",
            )
        )
