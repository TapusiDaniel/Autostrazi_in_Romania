from data.sections.a0_sections import A0_SECTIONS
from data.sections.a1_sections import A1_SECTIONS
from data.sections.a2_sections import A2_SECTIONS
from data.sections.a3_sections import A3_SECTIONS
from data.sections.a4_sections import A4_SECTIONS
from data.sections.a5_sections import A5_SECTIONS
from data.sections.a6_sections import A6_SECTIONS
from data.sections.a7_sections import A7_SECTIONS
from data.sections.a8_sections import A8_SECTIONS
from data.sections.a9_sections import A9_SECTIONS
from data.sections.a10_sections import A10_SECTIONS
from data.sections.a13_sections import A13_SECTIONS
from data.sections.dex12_sections import DEx12_SECTIONS
from data.sections.dex4_sections import DEx4_SECTIONS
from data.sections.dex5a_sections import DEx5A_SECTIONS
from data.sections.dex6_sections import DEx6_SECTIONS
from data.sections.dex8_sections import DEx8_SECTIONS
from data.sections.dex16_sections import DEx16_SECTIONS
from data.sections.buzau_braila_sections import Buzau_Braila_SECTIONS
from data.sections.tisita_albita_sections import Tisita_Albita_SECTIONS
from data.sections.gaesti_ploiesti_sections import Gaesti_Ploiesti_SECTIONS
from data.sections.bucuresti_targoviste_sections import Bucuresti_Targoviste_SECTIONS
from data.sections.suceava_botosani_sections import Suceava_Botosani_SECTIONS
from data.sections.dex4_jibou_romanasi_sections import DEx4_JIBOU_ROMANASI_SECTIONS
from data.sections.dex14_sections import DEx14_SECTIONS
from data.sections.dex_pitesti_mioveni_sections import DEx_PITESTI_MIOVENI_SECTIONS
from data.sections.dex_drumuri_radiale_sections import DEx_DRUMURI_RADIALE_SECTIONS
import os

HIGHWAYS = {
    "A0": {
        "name": "Centura București",
        "sections": A0_SECTIONS,
        "color": "green",
        "total_length": "100.7 km"
    },
    "A1": {
        "name": "Autostrada București - Nădlac",
        "sections": A1_SECTIONS,
        "color": "green",
        "total_length": "578.48 km"
    },
    "A2": {
        "name": "Autostrada Soarelui",
        "sections": A2_SECTIONS,
        "color": "green",
        "total_length": "202.79 km"
    },
    "A3": {
        "name": "Autostrada Transilvania",
        "sections": A3_SECTIONS,
        "color": "green",
        "total_length": "438 km"
    },
    "A4": {
        "name": "Constanța Bypass",
        "sections": A4_SECTIONS,
        "color": "green",
        "total_length": "52.39 km"
    },
    "A5": {
        "name": "Autostrada Sudului",
        "sections": A5_SECTIONS,
        "color": "green",
        "total_length": "125.8 km"
    },
    "A6": {
        "name": "Autosrada Sud",
        "sections": A6_SECTIONS,
        "color": "green",
        "total_length": "450 km"
    },
    "A7": {
        "name": "Autosrada Moldovei",
        "sections": A7_SECTIONS,
        "color": "green",
        "total_length": "437 km"
    },
    "A8": {
        "name": "Autosrada Unirii",
        "sections": A8_SECTIONS,
        "color": "green",
        "total_length": "307.88 km"
    },
    "A9": {
        "name": "Autosrada Timișoara - Moravița",
        "sections": A9_SECTIONS,
        "color": "green",
        "total_length": "72.93 km"
    },
    "A10": {
        "name": "Autosrada Sebeș - Turda",
        "sections": A10_SECTIONS,
        "color": "green",
        "total_length": "70 km"
    },
    "A13": {
        "name": "Autosrada Sibiu - Bacău",
        "sections": A13_SECTIONS,
        "color": "green",
        "total_length": "300 km"
    },
    "DEx12": {
            "name": "Drumul Expres Craiova - Pitești",
            "sections": DEx12_SECTIONS,
            "color": "green",
            "total_length": "121.25 km"
    },
    "DEx4": {
            "name": "Drumul Expres Turda - Dej",
            "sections": DEx4_SECTIONS,
            "color": "green",
            "total_length": "70 km"
    },
    "DEx5A": {
            "name": "Drumul Expres DEx5A Bacău - Piatra Neamț",
            "sections": DEx5A_SECTIONS,
            "color": "green",
            "total_length": "51 km"
    },
    "DEx6": {
            "name": "Drumul Expres Focșani - Brăila - Galați",
            "sections": DEx6_SECTIONS,
            "color": "green",
            "total_length": "85.81 km"
    },
    "DEx8": {
            "name": "Drumul Expres Constanța - Tulcea - Brăila",
            "sections": DEx8_SECTIONS,
            "color": "green",
            "total_length": "172 km"
    },
    "DEx16": {
            "name": "Drumul Expres Arad - Oradea",
            "sections": DEx16_SECTIONS,
            "color": "green",
            "total_length": "136.97 km"
    },
    "Buzău - Brăila": {
            "name": "Drumul Expres Buzău - Brăila",
            "sections": Buzau_Braila_SECTIONS,
            "color": "green",
            "total_length": "94 km"
    },
    "Tișița - Albița": {
            "name": "Drumul Expres Tișița - Albița",
            "sections": Tisita_Albita_SECTIONS,
            "color": "green",
            "total_length": "~ 160 km"
    },
    "Găești - Ploiești": {
            "name": "Drumul Expres Găești - Ploiești",
            "sections":Gaesti_Ploiesti_SECTIONS,
            "color": "green",
            "total_length": "~ 81.5 km"
    },
    "București - Târgoviște": {
            "name": "Drumul Expres București - Târgoviște",
            "sections":Bucuresti_Targoviste_SECTIONS,
            "color": "green",
            "total_length": "~ 62 km"
    },
    "Suceava - Botoșani": {
            "name": "Drumul Expres Suceava - Botoșani",
            "sections":Suceava_Botosani_SECTIONS,
            "color": "green",
            "total_length": "~ 20 km"
    },
    "Jibou - Românași": {
            "name": "Drumul Expres Jibou – Românași (DEx4), legătura la Autostrada Transilvania",
            "sections":DEx4_JIBOU_ROMANASI_SECTIONS,
            "color": "green",
            "total_length": "~ 20 km"
    },
    "DEx14": {
            "name": "Autostrada Nordului",
            "sections":DEx14_SECTIONS,
            "color": "green",
            "total_length": "335 km"
    },
    "Pitești - Mioveni": {
            "name": "Drumul Expres Dacia",
            "sections":DEx_PITESTI_MIOVENI_SECTIONS,
            "color": "green",
            "total_length": "10.39 km"
    },
    "Drumuri Radiale": {
            "name": "Drumuri Radiale",
            "sections":DEx_DRUMURI_RADIALE_SECTIONS,
            "color": "green",
            "total_length": "96.11 km"
    },
}
