import json
from typing import List, Dict, Any, Optional

class Alignment:
    def __init__(self, data: Dict[str, Any]):
        self.good_evil_axis = data.get("good_evil_axis", "")
        self.law_chaos_axis = data.get("law_chaos_axis", "")

class Obedience:
    def __init__(self, data: Dict[str, Any]):
        self.ritual = data.get("ritual", "")
        self.boon = data.get("boon", "")

class AsAdventurers:
    def __init__(self, data: Dict[str, Any]):
        self.desc = data.get("desc", "")
        self.motivations = data.get("motivations", [])
        self.common_classes = data.get("common_classes", [])

class WorshipedBy:
    def __init__(self, data: Dict[str, Any]):
        self.common_faithful = data.get("common_faithful", [])
        self.as_adventurers = AsAdventurers(data.get("as_adventurers", {}))
        self.main_regions = data.get("main_regions", [])
        self.restricted_groups = data.get("restricted_groups", [])

class Temples:
    def __init__(self, data: Dict[str, Any]):
        self.common_locations = data.get("common_locations", [])
        self.designs = data.get("designs", "")
        self.functions = data.get("functions", [])

class Shrines:
    def __init__(self, data: Dict[str, Any]):
        self.common_locations = data.get("common_locations", [])
        self.designs = data.get("designs", "")
        self.functions = data.get("functions", [])

class PaladinCode:
    def __init__(self, data: Dict[str, Any]):
        self.name_of_code = data.get("name_of_code", "")
        self.codes = data.get("codes", [])

class HolyText:
    def __init__(self, data: Dict[str, Any]):
        self.name_of_text = data.get("name_of_text", "")
        self.desc_of_text = data.get("desc_of_text", "")

class Holiday:
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get("name", "")
        self.when_it_happens = data.get("when_it_happens", "")
        self.why_it_happens = data.get("why_it_happens", "")
        self.how_to_celebrate = data.get("how_to_celebrate", "")

class Aphorism:
    def __init__(self, data: Dict[str, Any]):
        self.expression = data.get("expression", "")
        self.meaning = data.get("meaning", "")

class MainChurch:
    def __init__(self, data: Dict[str, Any]):
        self.name_of_faith = data.get("name_of_faith", "")
        self.priest_main_role = data.get("priest_main_role", "")
        self.church_structure = data.get("church_structure", [])
        self.temples = Temples(data.get("temples", {}))
        self.shrines = Shrines(data.get("shrines", {}))
        self.clothing_desc_of_clergy = data.get("clothing_desc_of_clergy", "")
        self.paladin_code = PaladinCode(data.get("paladin_code", {}))
        self.holy_text = [HolyText(ht) for ht in data.get("holy_text", [])]
        self.holidays = [Holiday(h) for h in data.get("holidays", [])]
        self.aphorisms = [Aphorism(a) for a in data.get("aphorisms", [])]

class Orthodoxy:
    def __init__(self, data: Dict[str, Any]):
        self.quote = data.get("quote", "")
        self.alignment = Alignment(data.get("alignment", {}))
        self.name_of_orthodoxy = data.get("name_of_orthodoxy", "")
        self.overview = data.get("overview", "")
        self.differences_from_main = data.get("differences_from_main", [])
        self.priest_main_role = data.get("priest_main_role", "")
        self.church_structure = data.get("church_structure", [])
        self.temples = Temples(data.get("temples", {}))
        self.shrines = Shrines(data.get("shrines", {}))
        self.clothing_desc_of_clergy = data.get("clothing_desc_of_clergy", "")
        self.paladin_code = PaladinCode(data.get("paladin_code", {}))
        self.holy_text = [HolyText(ht) for ht in data.get("holy_text", [])]
        self.common_holidays = [Holiday(h) for h in data.get("common_holidays", [])]
        self.different_holidays = [Holiday(h) for h in data.get("different_holidays", [])]
        self.aphorisms = [Aphorism(a) for a in data.get("aphorisms", [])]

class HomeRealm:
    def __init__(self, data: Dict[str, Any]):
        self.name_of_realm = data.get("name_of_realm", "")
        self.desc_of_realm = data.get("desc_of_realm", "")
        self.role_of_the_dead = data.get("role_of_the_dead", "")

class PlanarAlly:
    def __init__(self, data: Dict[str, Any]):
        self.name_of_ally = data.get("name_of_ally", "")
        self.title_of_ally = data.get("title_of_ally", "")
        self.physical_desc_of_ally = data.get("physical_desc_of_ally", "")
        self.role_of_ally = data.get("role_of_ally", "")

class Knowledge:
    def __init__(self, data: Dict[str, Any]):
        self.common_knowledge = data.get("common_knowledge", [])
        self.secret_knowledge = data.get("secret_knowledge", [])
        self.godly_knowledge = data.get("godly_knowledge", [])
        self.player_knowledge = data.get("player_knowledge", [])
        self.dm_knowledge = data.get("dm_knowledge", [])

class Deity:
    def __init__(self):
        self.id = None  # This will be set when loading from DB
        self.name: str = ""
        self.nicknames: List[str] = []
        self.overview: str = ""
        self.alignment: Optional[Alignment] = None
        self.domains: List[str] = []
        self.subdomains: List[str] = []
        self.holy_symbol: str = ""
        self.favored_weapon: str = ""
        self.sacred_animal: str = ""
        self.symbolic_elements: List[str] = []
        self.centers_of_worship: List[str] = []
        self.worshiped_by: Optional[WorshipedBy] = None
        self.avatars: List[str] = []
        self.obedience: Optional[Obedience] = None
        self.taboos: List[str] = []
        self.understanding_the_deity: str = ""
        self.pantheon: str = ""
        self.main_church: Optional[MainChurch] = None
        self.orthodoxies: List[Orthodoxy] = []
        self.home_realm: Optional[HomeRealm] = None
        self.planar_allies: List[PlanarAlly] = []
        self.associated_creatures: List[str] = []
        self.antagonists_and_rivals: List[str] = []
        self.knowledge: Optional[Knowledge] = None

    def load_from_dict(self, data: Dict[str, Any]):
        self.name = data.get("name", "")
        self.nicknames = data.get("nicknames", [])
        self.overview = data.get("overview", "")
        self.alignment = Alignment(data.get("alignment", {}))
        self.domains = data.get("domains", [])
        self.subdomains = data.get("subdomains", [])
        self.holy_symbol = data.get("holy_symbol", "")
        self.favored_weapon = data.get("favored_weapon", "")
        self.sacred_animal = data.get("sacred_animal", "")
        self.symbolic_elements = data.get("symbolic_elements", [])
        self.centers_of_worship = data.get("centers_of_worship", [])
        self.worshiped_by = WorshipedBy(data.get("worshiped_by", {}))
        self.avatars = data.get("avatars", [])
        self.obedience = Obedience(data.get("obedience", {}))
        self.taboos = data.get("taboos", [])
        self.understanding_the_deity = data.get("understanding_the_deity", "")
        self.pantheon = data.get("pantheon", "")
        self.main_church = MainChurch(data.get("main_church", {}))
        self.orthodoxies = [Orthodoxy(o) for o in data.get("orthodoxies", [])]
        self.home_realm = HomeRealm(data.get("home_realm", {}))
        self.planar_allies = [PlanarAlly(a) for a in data.get("planar_allies", [])]
        self.associated_creatures = data.get("associated_creatures", [])
        self.antagonists_and_rivals = data.get("antagonists_and_rivals", [])
        self.knowledge = Knowledge(data.get("knowledge", {}))

    def load_from_json(self, json_str: str):
        data = json.loads(json_str)
        self.load_from_dict(data)

   