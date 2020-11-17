"""
This file contains lists of words whose embeddings we want to look at,
and dictionaries that map singular nouns to their pural forms. 
TODO
- add words for denial of agency
"""

all_vermin_singulars = [
    "vermin", 
    "rodent", 
    "rat", 
    "mouse", 
    "cockroach", 
    "termite", 
    "bedbug", 
    "fleas"
]

all_vermin_plurals_dict = {
    "rodent" : ["rodents"],
    "rat" : ["rats"],
    "termite" : ["termites"],
    "bedbug" : ["bedbugs"],
    "cockroach" : ["cockroaches"], 
    "mouse" : ["mice"]
}

all_moral_disgust_stem = [
    "american"
]

all_moral_disgust_dict = {
    "american" : ["americans"]
}

# all_moral_disgust_stem = [
#     "disgust",
#     "disease",
#     "unclean",
#     "contagious",
#     "sin",
#     "slut",
#     "whore",
#     "dirt",
#     "impiety",
#     "profane",
#     "gross",
#     "repulsive",
#     "sick",
#     "promiscuous",
#     "lewd",
#     "aduterate",
#     "tramp",
#     "prostitute",
#     "unchaste",
#     "intemperate",
#     "wanton",
#     "profligate",
#     "filth",
#     "trash",
#     "obscene",
#     "lax",
#     "taint",
#     "stain",
#     "tarnish",
#     "debase",
#     "wicked",
#     "blemish",
#     "exploit",
#     "pervert",
#     "wretched"
# ]

# # Each word is mapped to a list of related words
# all_moral_disgust_dict = {
#     "disgust" : ["disgusting"],
#     "contagious" : ["contagion"],
#     "sin" : ["sinful", "sinner", "sins", "sinned", "sinning"],
#     "slut" : ["slutty"],
#     "dirt" : ["dirty"],
#     "impiety" : ["impious"],
#     "profane" : ["profanity"],
#     "sick" : ["sickness"],
#     "lewd" : ["lewding"],
#     "tramp" : ["tramps"],
#     "prostitute" : ["prostitution"],
#     "filth" : ["filthy"],
#     "trash" : ["trashy"],
#     "obscene" : ["obscenity"],
#     "exploit" : ["exploitative"]
# }

all_target_singulars = [
    "gay",
    "lesbian",
    "bisexual",
    "homosexual",
    "transgender",
    "transsexual",
    "transexual",
    "transvestite",
    "transgendered",
    "asexual",
    "agender",
    "aromantic",
    "lgb",
    "lgbt",
    "lgbtq",
    "lgbtqia",
    "glbt",
    "lgbtqqia", 
    "genderqueer", 
    "genderfluid", 
    "intersex", 
    "pansexual"
]

all_target_plurals_dict = {
    "gay" : ["gays"],
    "lesbian" : ["lesbians"], 
    "bisexual" : ["bisexuals"],
    "homosexual" : ["homosexuals"],
    "transgender" : ["transgenders"],
    "transsexual" : ["transsexuals"],
    "transexual" : ["transexuals"],
    "transvestite" : ["transvestites"]
}