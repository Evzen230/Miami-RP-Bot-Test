
# === SEZNAMY DOSTUPNÝCH AUT A ZBRANÍ ===

# Role ID a týdenní odměna (v dolarech)
ROLE_ODMENY = {
    1293617189005557873: 3000,      #Občan
    1293617189005557870: 25000,     #Ředitel: FHP
    1293617189005557868: 25000,     #Ředitel: MPD
    1293617189005557867: 10000,     #Ředitel: MFD
    1293617189005557865: 10000,     #Ředitel: FDOT
    1293617189005557864: 25000,     #Ředitel: FBI
    1293617189005557866: 10000,     #Ředitel: EMS
    1293617189005557869: 9500,      #Ředitel: MGMC
    1346163519070146681: 9500,      #Ředitel: IRS
    1330524261030301707: 9500,      #Ředitel: DMV
}

# Auta na přidávání
DOSTUPNA_AUTA = [
    "Falcon Stallion 350 1969", "Bullhorn Prancer 1969",
    "Falcon Advance 100 Holiday Edition 1956", "Chevlon Corbeta C2 1967",
    "Sentinel Platinum 1968", "Bullhorn Foreman 1988",
    "Arrow Phoenix Nationals 1977", "Vellfire Runabout 1984",
    "Chevlon L/35 Extended 1981", "Chevlon Inferno 1981", "Chevlon L/15 1981",
    "Falcon Traveller 2003", "Chevlon Camion 2002", "Falcon Prime Eques 2003",
    "Vellfire Evertt 1995", "Overland Apache 1995", "Vellfire Prima 2009",
    "Overland Apache 2011", "Overland Buckaroo 2018", "Falcon Scavenger 2016",
    "Falcon Fission 2015", "Chevlon Captain 2009", "Vellfire Riptide 2020",
    "Bullhorn BH15 2009", "Elysion Slick 2014", "Chevlon Commuter Van 2006",
    "Chevlon Amigo LZR 2016", "Chevlon Landslide 2007",
    "Falcon Traveller 2022", "Navara Boundary 2022",
    "Bullhorn Determinator 2008", "Chevlon Camion 2021", "Chevlon Camion 2008",
    "Chevlon Revver 2005", "Falcon Rampage Bigfoot 2-Door 2021",
    "Bullhorn Prancer 2011", "Navara Imperium 2020", "Falcon Advance 2018",
    "Falcon Advance Beast 2017", "Falcon Rampage Beast 2021",
    "Falcon Advance 2022", "Bullhorn Prancer Widebody 2020",
    "Bullhorn Determinator SFP Fury 2022", "Vellfire Prairie 2022",
    "Bullhorn Pueblo 2018", "Navara Horizon 2013", "Chevlon Antilope 1994",
    "Leland LTS 2010", "Overland Apache SFP 2020", "Stuttgart Landschaft 2022",
    "Vellfire Pioneer 2019", "Falcon Stalion 350", "Chevlon Amigo S 2011",
    "Chevlon Amigo S 2016", "Amigo LZR 2011", "Averon S5 2010",
    "Leland Vault 2020", "Averon RS3 2020", "Stuttgart Executive 2021",
    "Terrain Traveller 2022", "Averon Q8 2022", "BKM Munich 2020",
    "Stuttgart Vierturig 2021", "Takeo Experience 2021", "Averon R8 2017",
    "Strugatti Ettore 2020", "Surrey 650S 2016", "LTS5-V Blackwing 2023",
    "Falcon Heritage 2021", "Ferdinand Jalapeno Turbo 2022",
    "Falcon Traveller 2022", "Chevlon Corbeta TZ 2014",
    "Chevlon Corbeta 8 2023", "Falcon Advance Bolt 2024", "Averon Anodic 2024",
    "Celestial Truckatron 2024", "BKM Risen Roadster 2020"
]

#Ceník aut
AUTA = {
    # Classic
    "Falcon Stallion 350 1969": {"cena": 260000, "role": None},
    "Bullhorn Prancer 1969": {"cena": 245000, "role": None},
    "Falcon Advance 100 Holiday Edition 1956": {"cena": 95000, "role": None},
    "Chevlon Corbeta C2 1967": {"cena": 185000, "role": None},
    "Sentinel Platinum 1968": {"cena": 115000, "role": None},
    "Bullhorn Foreman 1988": {"cena": 105000, "role": None},
    "Arrow Phoenix Nationals 1977": {"cena": 240000, "role": None},
    "Vellfire Runabout 1984": {"cena": 95000, "role": None},
    "Chevlon L/35 Extended 1981": {"cena": 105000, "role": None},
    "Chevlon Inferno 1981": {"cena": 97500, "role": None},
    "Chevlon L/15 1981": {"cena": 92000, "role": None},

    # Regular
    "Falcon Traveller 2003": {"cena": 15000, "role": None},
    "Chevlon Camion 2002": {"cena": 10000, "role": None},
    "Falcon Prime Eques 2003": {"cena": 9000, "role": None},
    "Vellfire Evertt 1995": {"cena": 20000, "role": None},
    "Overland Apache 1995": {"cena": 12000, "role": None},
    "Vellfire Prima 2009": {"cena": 10000, "role": None},
    "Overland Apache 2011": {"cena": 40000, "role": None},
    "Overland Buckaroo 2018": {"cena": 45000, "role": None},
    "Falcon Scavenger 2016": {"cena": 40000, "role": None},
    "Falcon Fission 2015": {"cena": 35000, "role": None},
    "Chevlon Captain 2009": {"cena": 20000, "role": None},
    "Vellfire Riptide 2020": {"cena": 55000, "role": None},
    "Bullhorn BH15 2009": {"cena": 30000, "role": None},
    "Elysion Slick 2014": {"cena": 20000, "role": None},
    "Chevlon Commuter Van 2006": {"cena": 30000, "role": None},
    "Chevlon Amigo LZR 2016": {"cena": 100000, "role": None},
    "Chevlon Landslide 2007": {"cena": 26000, "role": None},
    "Falcon Traveller 2022": {"cena": 90000, "role": None},
    "Navara Boundary 2022": {"cena": 65000, "role": None},
    "Bullhorn Determinator 2008": {"cena": 70000, "role": None},
    "Chevlon Camion 2021": {"cena": 75000, "role": None},
    "Chevlon Camion 2008": {"cena": 30000, "role": None},
    "Chevlon Revver 2005": {"cena": 50000, "role": None},
    "Falcon Rampage Bigfoot 2-Door 2021": {"cena": 70000, "role": None},
    "Bullhorn Prancer 2011": {"cena": 50000, "role": None},
    "Navara Imperium 2020": {"cena": 30000, "role": None},
    "Falcon Advance 2018": {"cena": 70000, "role": None},
    "Falcon Advance Beast 2017": {"cena": 100000, "role": None},
    "Falcon Rampage Beast 2021": {"cena": 130000, "role": None},
    "Falcon Advance 2022": {"cena": 140000, "role": None},
    "Bullhorn Prancer Widebody 2020": {"cena": 170000, "role": None},
    "Bullhorn Determinator SFP Fury 2022": {"cena": 185000, "role": None},
    "Vellfire Prairie 2022": {"cena": 80000, "role": None},
    "Bullhorn Pueblo 2018": {"cena": 100000, "role": None},
    "Navara Horizon 2013": {"cena": 250000, "role": None},
    "Chevlon Antilope 1994": {"cena": 7000, "role": None},
    "Leland LTS 2010": {"cena": 42000, "role": None},
    "Overland Apache SFP 2020": {"cena": 150000, "role": None},
    "Stuttgart Landschaft 2022": {"cena": 200000, "role": None},
    "Vellfire Pioneer 2019": {"cena": 125000, "role": None},
    "Falcon Stalion 350": {"cena": 100000, "role": None},
    "Chevlon Amigo S 2011": {"cena": 85000, "role": None},
    "Chevlon Amigo S 2016": {"cena": 96000, "role": None},
    "Chevlon Amigo LZR 2011": {"cena": 90000, "role": None},

    # Prestige
    "Averon S5 2010": {"cena": 140000, "role": None},
    "Leland Vault 2020": {"cena": 130000, "role": None},
    "Averon RS3 2020": {"cena": 180000, "role": None},
    "Stuttgart Executive: 2021": {"cena": 240000, "role": None},
    "Terrain Traveller 2022": {"cena": 180000, "role": None},
    "Averon Q8 2022": {"cena": 220000, "role": None},
    "BKM Munich 2020": {"cena": 185000, "role": None},
    "Stuttgart Vierturig: 2021": {"cena": 250000, "role": None},
    "Takeo Experience 2021": {"cena": 550000, "role": None},
    "Averon R8 2017": {"cena": 800000, "role": None},
    "Strugatti Ettore 2020": {"cena": 1200000, "role": None},
    "Surrey 650S 2016": {"cena": 900000, "role": None},
    "Leland LTS5-V Blackwing 2023": {"cena": 280000, "role": None},
    "Falcon Heritage 2021": {"cena": 720000, "role": None},
    "Ferdinand Jalapeno Turbo: 2022": {"cena": 200000, "role": None},
    "Chevlon Corbeta TZ 2014": {"cena": 450000, "role": None},
    "Chevlon Corbeta 8 2023": {"cena": 600000, "role": None},

    # Electric
    "Falcon Advance Bolt 2024": {"cena": 350000, "role": None},
    "Averon Anodic 2024": {"cena": 500000, "role": None},
    "Celestial Truckatron 2024": {"cena": 800000, "role": None},
    "BKM Risen Roadster 2020": {"cena": 650000, "role": None},

    #====PD Auta=====
    "Falcon Prime Eques 2003": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Captain PPV 2006": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Bullhorn Pueblo Pursuit 2018": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Amigo LZR 2011": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Interceptor Sedan 2017": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Bullhorn Prancer Pursuit 2011": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Stallion 350 2015": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Bullhorn Prancer Pursuit 2015": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Bullhorn Prancer Pursuit Widebody 2020": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Corbeta TZ 2014": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Bullhorn Determinator SFP Fury 2022": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Camion PPV 2008": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Camion PPV 2018": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Camion PPV 2021": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "BKM Munich 2020": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Rampage PPV 2021": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Traveller SSV 2022": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Interceptor Utility 2013": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Interceptor Utility 2019": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Interceptor Utility 2020": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Averon Q8 2022": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Advance SSV 2018": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Bullhorn BH15 SSV 2009": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Falcon Advance Bolt 2024": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Platoro PPV 2019": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "4-Wheeler": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Canyon Descender LEO": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Chevlon Commuter Van 2006": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Mobile Command 2005": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Prisoner Transport": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Emergency Services Falcon Advance+ 2020": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "SWAT Truck 2011": {'cena': 0, 'role': '1338975549711978568 || 1293617189005557870 || 1293617189005557868 || 1293617189005557864'},
    "Fire Engine": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Heavy Tanker": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Ladder Truck": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Heavy Rescue": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Special Operations Unit": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Bullhorn Ambulance": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "International Ambulance": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Medical Bus": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Canyon Descender": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "4 Wheeler": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Paramedic SUV": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "FD Chevlon Camion 2018": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Utility Falcon Advance+": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Squad Falcon Advance+ 2020": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Brush Falcon Advance+ 2020": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Falcon Advance": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "FD Bullhorn Prancer": {'cena': 0, 'role': '1293617189005557867 || 1293617189005557866'},
    "Mobile Command Center": {'cena': 0, 'role': '1293617189005557867 || 12936171890055557866'},
    "Vellfire Evertt Crew Cab 1995": {'cena': 0, 'role': '1293617189005557865'},
    "Flatbed Tow Truck": {'cena': 0, 'role': '1293617189005557865'},
    "Cone Truck": {'cena': 0, 'role': '1293617189005557865'},
    "Falcon Advance+ Tow Truck 2020": {'cena': 0, 'role': '1293617189005557865'},
    "Falcon Advance+ Roadside Assist 2020": {'cena': 0, 'role': '1293617189005557865'},
    "Chevlon Platoro Utility": {'cena': 0, 'role': '1293617189005557865'},
    "Bucket Truck": {'cena': 0, 'role': '1293617189005557865'},
    "Falcon Advance+ Utility": {'cena': 0, 'role': '1293617189005557865'},
    "Street Sweeper": {'cena': 0, 'role': '1293617189005557865'},
    "Salt Truck": {'cena': 0, 'role': '1293617189005557865'},
    "Traffic Light Trailer": {'cena': 0, 'role': '1293617189005557865'},
    "Traffic Arrow Trailer": {'cena': 0, 'role': '1293617189005557865'},
    "LED Message Board Trailer": {'cena': 0, 'role': '1293617189005557865'},
    "Asphalt Trailer": {'cena': 0, 'role': '1293617189005557865'},
    "Flood Light Trailer": {'cena': 0, 'role': '1293617189005557865'},
}

#Ceník zbraní
CENY_ZBRANI = {
    # Zbraně typu A:
    "Beretta M9": 700, 
    "Desert Eagle": 900, 
    "Colt M1911": 750, 
    "Colt Python": 1000,
    "Lemat Revolver": 1200,

    # Zbraně typu B:
    "TEC-9": 1000,
    "Skorpion": 1100,
    "Kriss Vector": 1500, 

    #Zbraně typu C:
    "M14": 2000,
    "AK47": 2500, 
    "PPSH 41": 2300, 
    "LMT L129A1": 2600, 
    "Remington 870": 2000, 

    #Zbraně typu D:
    "Remington MSR": 15000, 
    "M249":  12000 
}

#Zbraně na přidávání
DOSTUPNE_ZBRANE = [
    "Beretta M9", "M249", "Remington MSR", "M14", "AK47", "PPSH 41",
    "Desert Eagle", "Colt M1911", "Kriss Vector", "LMT L129A1", "Skorpion",
    "Colt Python", "TEC-9", "Remington 870", "Lemat Revolver"
]

#Věci na drogy a drogy
DOSTUPNE_VECI = ["Chemikálie", "Sušička", "UV Lampa", "Chemické nádobí", "Edrin", "MDMA", "Cukr", "Formička", "Mák"]

CENY_VECI = {
    # 🔬 Suroviny
    "Chemikálie": 200,
    "Edrin": 300,
    "Mdma prášek": 200,
    "Barvivo": 50,
    "Plnidlo": 40,
    "Pseudoefedrin": 180,
    "Čistič": 90,
    "Cukr": 50,
    "Máková pasta": 150,
    "Semena marihuany": 250,
    "Voda": 10,
    "Hnojivo": 30,
    "Ocet": 15,
    "Listy koky": 350,

    # 🛠️ Nástroje
    "Sušička": 1500,
    "Formička": 1000,
    "UV lampa": 1000,
    "Květináč": 150,
    "Destilační sada": 2500,
    "Extraktor": 2000,
    "Ochranná maska": 800,
    "Ochranné rukavice": 100,
    "Tabletovací lis": 3000,
    "Pěstební světlo": 1000,
    "Varná sada": 1800
}

DROGY = ["Marihuana", "Kokain", "Metamfetamin", "Pervitin", "Extáze", "Heroin"]

VYROBA_COOLDOWN = 2  # minutes

RECEPTY = {
    "Marihuana": {
        "suroviny": {
            "Semena marihuany": 1,
            "Voda": 2,
            "Hnojivo": 1
        },
        "nastroje": {
            "Květináč": 1,
            "UV Lampa": 1,
            "Sušička": 1
        },
        "cas": 5,  # minut za 10g
        "selhani": 0
    },
    "Kokain": {
        "suroviny": {
            "Listy koky": 3,
            "Chemikálie": 2
        },
        "nastroje": {
            "Extraktor": 1,
            "Ochranné rukavice": 1
        },
        "cas": 6,
        "selhani": 0.10
    },
    "Metamfetamin": {
        "suroviny": {
            "Chemikálie": 3,
            "Pseudoefedrin": 2
        },
        "nastroje": {
            "Destilační sada": 1,
            "Ochranné rukavice": 1
        },
        "cas": 7,
        "selhani": 0.12
    },
    "Pervitin": {
        "suroviny": {
            "Pseudoefedrin": 3,
            "Čistič": 1
        },
        "nastroje": {
            "Destilační sada": 1,
            "Ochranné rukavice": 1
        },
        "cas": 6,
        "selhani": 0.09
    },
    "Extáze": {
        "suroviny": {
            "MDMA prášek": 2,
            "Barvivo": 1,
            "Plnidlo": 1
        },
        "nastroje": {
            "Formička": 1,
            "Ochranné rukavice": 1
        },
        "cas": 5,
        "selhani": 0.07
    },
    "Heroin": {
        "suroviny": {
            "Mák": 2,
            "Ocet": 1,
            "Chemikálie": 1
        },
        "nastroje": {
            "Destilační sada": 1,
            "Ochranná maska": 1
        },
        "cas": 7,
        "selhani": 0.11
    }
}

UCINKY_DROG = {
    "Marihuana": {
        "base": "🧘 Uklidnění a zpomalení reakcí",
        "priznaky": [
            "👁️‍🗨️ Zarudlé oči", 
            "🍔 Zvýšená chuť k jídlu",
            "😶 Zpomalená řeč"
        ],
        "trvani": 5
    },
    "Kokain": {
        "base": "⚡ Zvýšená energie a euforie",
        "priznaky": [
            "👃 Časté čichání", 
            "👁️ Rozšířené zornice",
            "💦 Pocení"
        ],
        "trvani": 8
    },
    "Metamfetamin": {
        "base": "🔥 Extrémní bdělost a hyperaktivita",
        "priznaky": [
            "💢 Paranoia", 
            "👄 Rychlé mluvení",
            "💦 Pocení"
        ],
        "trvani": 10
    },
    "Pervitin": {
        "base": "🌀 Silná euforie a soustředění",
        "priznaky": [
            "😬 Skřípání zubů",
            "💧 Sucho v ústech",
            "👁️ Rozšířené zornice"
        ],
        "trvani": 10
    },
    "Extáze": {
        "base": "💖 Emoční propojení a euforie",
        "priznaky": [
            "👁️ Velké zornice",
            "💦 Pocení",
            "🤗 Přehnaná empatie"
        ],
        "trvani": 7
    },
    "Heroin": {
        "base": "😴 Uklidnění a utlumení bolesti",
        "priznaky": [
            "😵 Zúžené zornice",
            "🛌 Malátnost",
            "🩸 Pomalejší dýchání"
        ],
        "trvani": 12
    },
}

# 📦 Seznam věcí pro autocomplete (z cen)
VECI_SEZNAM = list(CENY_VECI.keys())

# 📋 Seznam drog (přizpůsob podle svých receptů)
DROGY_SEZNAM = ["Marihuana", "Kokain", "Metamfetamin", "Pervitin", "Extáze", "Heroin"]

# Configuration constants
ADMIN_ROLE_ID = 1378111107780313209
POLICE_ROLE_ID = 1378711315119607808
LOG_CHANNEL_ID = 1293617189055758433
DATA_FILE = "data.json"
