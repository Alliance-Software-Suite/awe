import typing

import toml


class Infra(typing.TypedDict):
    max: int
    per_city: typing.Dict[int, int]


class Land(typing.TypedDict):
    min: int
    per_city: typing.Dict[int, int]


class Conf(typing.TypedDict):
    key: str

    nations: typing.List[int]
    alliances: typing.List[int]
    applicants: bool

    mmr: str
    mil_cap: float

    infra: Infra
    land: Land

    stats: bool


def get_config(args) -> Conf:
    with open(args.config) as f:
        cfg = toml.load(f, _dict=Conf)

    cfg.setdefault("key", "")

    cfg.setdefault("nations", [])
    cfg.setdefault("alliances", [])

    cfg.setdefault("mmr", "0000")
    cfg.setdefault("mil_cap", 0.0)

    cfg.setdefault("infra", Infra(max=-1, per_city={}))
    cfg["infra"].setdefault("max", -1)
    cfg["infra"].setdefault("per_city", {})

    cfg.setdefault("land", Land(min=-1, per_city={}))
    cfg["land"].setdefault("max", -1)
    cfg["land"].setdefault("per_city", {})

    if args.key is not None:
        cfg["key"] = args.key
    if args.nations is not None:
        cfg["nations"] = args.nations
    if args.alliances is not None:
        cfg["alliances"] = args.alliances
    cfg["applicants"] = args.applicants
    if args.mmr is not None:
        cfg["mmr"] = args.mmr
    if args.mil_cap is not None:
        cfg["mil_cap"] = args.mil_cap
    if args.infra is not None:
        cfg["infra"]["max"] = args.infra
    if args.land is not None:
        cfg["land"]["min"] = args.land
    cfg["stats"] = args.stats

    return cfg
