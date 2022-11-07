import json

import tabulate
from graphqlclient import GraphQLClient

from .cfg import Conf


def request(client, query):
    for nation in json.loads(
        client.execute(
            f"query{{nations({query},first:500)"
            f"{{data{{id,nation_name,alliance_position,num_cities,cities{{barracks,factory,hangar,drydock}}soldiers,tanks,aircraft,ships}}}}}}"
        )
    )["data"]["nations"]["data"]:
        yield nation


def m2s(m):
    return "".join([str(v) for v in m])


def m2c(mil, scale=1):
    return [m * c * scale for m, c in zip(mil, (3000, 250, 15, 5))]


def do_audit(cfg: Conf) -> None:
    client = GraphQLClient(
        "https://api.politicsandwar.com/graphql?api_key=" + cfg["key"]
    )

    if len(cfg["nations"]) != 0 and len(cfg["alliances"]) != 0:
        raise RuntimeError("-n/--nation and -a/--alliance are mutually exclusive.")
    if len(cfg["nations"]) != 0:
        if cfg["applicants"]:
            raise RuntimeError("-A/--applicants cannot be used with -n/--nation.")
        query = f"id:{cfg['nations']}"
    elif len(cfg["alliances"]) != 0:
        query = f"alliance_id:{cfg['alliances']}"
    else:
        raise RuntimeError("One of -n/--nation or -a/--alliance must be included.")

    output = []

    stats_total_nations = 0
    stats_total_violators = 0
    stats_total_mil = [0] * 4
    stats_total_soldiers = 0
    stats_total_tanks = 0
    stats_total_aircraft = 0
    stats_total_ships = 0
    stats_total_cities = 0

    for nation in request(client, query):
        if nation["alliance_position"] == "APPLICANT" and not cfg["applicants"]:
            continue

        stats_total_nations += 1

        result = []

        def add_result(s):
            nonlocal stats_total_violators

            if len(result) == 0:
                stats_total_violators += 1
                result.append(f"{nation['nation_name']} ({nation['id']})")
            result.append(s)

        stats_total_cities += nation["num_cities"]

        mmr = tuple(int(unit) for unit in cfg["mmr"])

        total_mil = [0] * 4
        max_mil = [0] * 4
        min_mil = [5] * 4
        for city in nation["cities"]:
            mil = (city["barracks"], city["factory"], city["hangar"], city["drydock"])
            for i, m in enumerate(mil):
                total_mil[i] += m
                stats_total_mil[i] += m
                if max_mil[i] < m:
                    max_mil[i] = m
                if min_mil[i] > m:
                    min_mil[i] = m

        avg_mil = [round(m / nation["num_cities"]) for m in total_mil]
        if any(m < mmr[i] for i, m in enumerate(avg_mil)):
            add_result(
                "MMR Violation\n"
                + tabulate.tabulate(
                    [[m2s(avg_mil), m2s(min_mil), m2s(max_mil)]],
                    headers=["Average", "Minimum", "Maximum"],
                    stralign="center",
                    numalign="center",
                )
            )

        stats_total_soldiers += nation["soldiers"]
        stats_total_tanks += nation["tanks"]
        stats_total_aircraft += nation["aircraft"]
        stats_total_ships += nation["ships"]
        mil_cap = m2c(mmr, nation["num_cities"])
        mil_real = [
            nation["soldiers"],
            nation["tanks"],
            nation["aircraft"],
            nation["ships"],
        ]
        if any(cap * cfg["mil_cap"] > real for cap, real in zip(mil_cap, mil_real)):
            add_result(
                "Military Capacity Unreached\n"
                + tabulate.tabulate(
                    [
                        [
                            str(round(real / cap * 100)) + "%"
                            for real, cap in zip(mil_real, mil_cap)
                        ]
                    ],
                    headers=["Soldiers", "Tanks", "Aircraft", "Ships"],
                )
            )

        if len(result) != 0:
            output.append("\n".join(result))

    if cfg["stats"]:
        output.append("=" * 64)
        stats_avg_mil = [round(v / stats_total_cities) for v in stats_total_mil]
        output.append(
            "Statistics\n"
            + tabulate.tabulate(
                [
                    [
                        stats_total_nations,
                        stats_total_violators,
                        stats_total_cities,
                        m2s(stats_avg_mil),
                        *[
                            str(round(real / cap * 100)) + "%"
                            for real, cap in zip(
                                [
                                    stats_total_soldiers,
                                    stats_total_tanks,
                                    stats_total_aircraft,
                                    stats_total_ships,
                                ],
                                m2c(stats_total_mil),
                            )
                        ],
                    ]
                ],
                headers=[
                    "Nations Checked",
                    "Nations Violating",
                    "Total Cities",
                    "Average Military Build",
                    "Barracks Utilization",
                    "Factory Utilization",
                    "Hangar Utilization",
                    "Drydock Utilization",
                ],
                stralign="center",
                numalign="center",
            )
        )

    print("\n\n".join(output))
