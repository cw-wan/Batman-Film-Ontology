import pandas as pd
import re
from rdflib import (
    Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef, BNode
)
from rdflib.collection import Collection

##############################################################################
# 1) Set up ontology namespace and base IRI
##############################################################################

ONTO_IRI = "http://www.semanticweb.org/charleswan/ontologies/batman-ontology"
BASE = Namespace(ONTO_IRI + "#")

# Create an RDF graph
g = Graph()

# Bind common prefixes for readability
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)
g.bind("", BASE)  # default prefix to our base

##############################################################################
# 2) Declare this as an OWL ontology
##############################################################################

ontology_uri = URIRef(ONTO_IRI)
g.add((ontology_uri, RDF.type, OWL.Ontology))

##############################################################################
# 3) Declare Classes (owl:Class) and subclass relationships
##############################################################################

Film = BASE.Film
ProductionCompany = BASE.ProductionCompany
Human = BASE.Human
Director = BASE.Director
Writer = BASE.Writer
Actor = BASE.Actor
Date = BASE.Date

# Mark them as owl:Class
for cls in (Film, ProductionCompany, Human, Director, Writer, Actor, Date):
    g.add((cls, RDF.type, OWL.Class))

# Director/Writer/Actor are subclasses of Human
g.add((Director, RDFS.subClassOf, Human))
g.add((Writer, RDFS.subClassOf, Human))
g.add((Actor, RDFS.subClassOf, Human))

##############################################################################
# 4) Declare Object Properties (owl:ObjectProperty) with domain & range
##############################################################################

hasDirector = BASE.hasDirector
hasActor = BASE.hasActor
isProducedBy = BASE.isProducedBy
hasStoryWriter = BASE.hasStoryWriter
hasScreenplayWriter = BASE.hasScreenplayWriter
hasCharacterWriter = BASE.hasCharacterWriter
hasReleaseDate = BASE.hasReleaseDate

object_properties = [
    (hasDirector, Film, Director),
    (hasActor, Film, Actor),
    (isProducedBy, Film, ProductionCompany),
    (hasStoryWriter, Film, Writer),
    (hasScreenplayWriter, Film, Writer),
    (hasCharacterWriter, Film, Writer),
    (hasReleaseDate, Film, Date),
]

for (prop, d, r) in object_properties:
    g.add((prop, RDF.type, OWL.ObjectProperty))
    g.add((prop, RDFS.domain, d))
    g.add((prop, RDFS.range, r))

##############################################################################
# 5) Declare Datatype Properties (owl:DatatypeProperty)
#    We'll store the domain/range via code or simply rely on usage
##############################################################################

hasTitle = BASE.hasTitle
hasRating = BASE.hasRating
hasRuntime = BASE.hasRuntime
hasImdbRating = BASE.hasImdbRating
hasRottenTomatoScore = BASE.hasRottenTomatoScore
hasMetascore = BASE.hasMetascore
hasYearProp = BASE.hasYear
hasMonthProp = BASE.hasMonth
hasDayProp = BASE.hasDay

for dp in (
        hasTitle, hasRating, hasRuntime, hasImdbRating,
        hasRottenTomatoScore, hasMetascore, hasYearProp, hasMonthProp, hasDayProp
):
    g.add((dp, RDF.type, OWL.DatatypeProperty))

# Also a "name" property for Film/ProductionCompany/Human
nameProp = BASE.name
g.add((nameProp, RDF.type, OWL.DatatypeProperty))
g.add((nameProp, RDFS.range, XSD.string))

# Make nameProp domain = Film OR ProductionCompany OR Human, using owl:unionOf
domain_union = BNode()
g.add((domain_union, RDF.type, OWL.Class))
collection_node = BNode()
union_list = Collection(g, collection_node)
union_list.append(Film)
union_list.append(ProductionCompany)
union_list.append(Human)
g.add((domain_union, OWL.unionOf, collection_node))
g.add((nameProp, RDFS.domain, domain_union))

##############################################################################
# 6) Read CSV
##############################################################################

df = pd.read_csv("batman_films.csv")


def slugify(text):
    """Convert a string to a URI-friendly slug."""
    return text.strip().lower().replace(" ", "_").replace(".", "").replace(",", "")


def parse_date(datestr):
    """Parse 'M/D/YYYY' -> (year, month, day). Return integers or None."""
    try:
        parts = datestr.strip().split('/')
        if len(parts) == 3:
            month, day, year = parts
            return int(year), int(month), int(day)
    except:
        pass
    return None, None, None


def parse_writers(writer_str):
    """Split the writer field into (name, role) pairs."""
    segments = [seg.strip() for seg in writer_str.split(',')]
    results = []
    for seg in segments:
        if '(' in seg and ')' in seg:
            namepart, rolepart = seg.split('(', 1)
            name = namepart.strip()
            role = rolepart.strip(' )').lower()
            results.append((name, role))
        else:
            name = seg.strip()
            if name:
                results.append((name, ""))
    return results


def parse_int_in_string(s):
    """
    Attempt to extract digits from the string and convert to int.
    E.g., 'PG-13' => 13, '84%' => 84, '140 min' => 140, etc.
    Returns None if no digits found or parse fails.
    """
    match = re.search(r'\d+', s)
    if match:
        try:
            return int(match.group())
        except:
            return None
    return None


# Dictionary for reusing the same person resource
people_dict = {}


def get_person_resource(name):
    """Return a single URI resource for each unique person's name."""
    key = slugify(name)
    if key not in people_dict:
        people_dict[key] = BASE["person_" + key]
    return people_dict[key]


##############################################################################
# 7) Build Individuals, set typed properties
##############################################################################

for idx, row in df.iterrows():
    film_title = str(row["Title"])
    film_year = str(row["Year"])

    # Create a Film individual
    film_id = slugify(film_title + "_" + film_year)
    film_uri = BASE[film_id]
    g.add((film_uri, RDF.type, Film))

    # hasTitle: string
    g.add((film_uri, hasTitle, Literal(film_title, datatype=XSD.string)))

    # hasRating: parse out digits from row["Rated"] => integer
    rating_val = parse_int_in_string(str(row["Rated"]))
    if rating_val is not None:
        g.add((film_uri, hasRating, Literal(rating_val, datatype=XSD.integer)))

    # hasRuntime: parse out digits from e.g. "140 min"
    runtime_val = parse_int_in_string(str(row["Runtime"]))
    if runtime_val is not None:
        g.add((film_uri, hasRuntime, Literal(runtime_val, datatype=XSD.integer)))

    # hasImdbRating -> float if you still want IMDb rating as float
    try:
        imdb_val = float(row["Imdb Rating"])
        g.add((film_uri, hasImdbRating, Literal(imdb_val, datatype=XSD.float)))
    except:
        pass

    # hasRottenTomatoScore: parse out digits from e.g. "84%"
    rts_val = parse_int_in_string(str(row["RottenTomatoScore"]))
    if rts_val is not None:
        g.add((film_uri, hasRottenTomatoScore, Literal(rts_val, datatype=XSD.integer)))

    # hasMetascore: integer
    try:
        meta_val = int(row["Metascore"])
        g.add((film_uri, hasMetascore, Literal(meta_val, datatype=XSD.integer)))
    except:
        pass

    # "name" for the Film
    g.add((film_uri, nameProp, Literal(film_title, datatype=XSD.string)))

    # Release date as an object property to a Date individual
    year_val, month_val, day_val = parse_date(str(row["Released"]))
    if year_val is not None:
        date_id = "releaseDate_" + film_id
        date_uri = BASE[date_id]
        g.add((date_uri, RDF.type, Date))
        g.add((film_uri, hasReleaseDate, date_uri))
        # hasYear, hasMonth, hasDay -> all integers
        g.add((date_uri, hasYearProp, Literal(year_val, datatype=XSD.integer)))
        g.add((date_uri, hasMonthProp, Literal(month_val, datatype=XSD.integer)))
        g.add((date_uri, hasDayProp, Literal(day_val, datatype=XSD.integer)))

    # Directors (hasDirector -> Person)
    directors = [d.strip() for d in str(row["Director"]).split(',') if d.strip()]
    for d in directors:
        person_uri = get_person_resource(d)
        g.add((person_uri, RDF.type, Director))
        # name for that person
        g.add((person_uri, nameProp, Literal(d, datatype=XSD.string)))
        # link from film
        g.add((film_uri, hasDirector, person_uri))

    # Actors (hasActor -> Person)
    actors = [a.strip() for a in str(row["Actors"]).split(',') if a.strip()]
    for a in actors:
        person_uri = get_person_resource(a)
        g.add((person_uri, RDF.type, Actor))
        g.add((person_uri, nameProp, Literal(a, datatype=XSD.string)))
        g.add((film_uri, hasActor, person_uri))

    # Production companies (isProducedBy -> ProductionCompany)
    companies = [c.strip() for c in str(row["Production"]).split(',') if c.strip()]
    for comp in companies:
        comp_slug = slugify(comp)
        comp_uri = BASE["company_" + comp_slug]
        g.add((comp_uri, RDF.type, ProductionCompany))
        g.add((comp_uri, nameProp, Literal(comp, datatype=XSD.string)))
        g.add((film_uri, isProducedBy, comp_uri))

    # Writers
    writer_str = str(row["Writer"])
    for wname, wrole in parse_writers(writer_str):
        if wname:
            w_uri = get_person_resource(wname)
            g.add((w_uri, RDF.type, Writer))
            g.add((w_uri, nameProp, Literal(wname, datatype=XSD.string)))
            wrole_lc = wrole.lower()
            if "story" in wrole_lc:
                g.add((film_uri, hasStoryWriter, w_uri))
            elif "screenplay" in wrole_lc:
                g.add((film_uri, hasScreenplayWriter, w_uri))
            elif "character" in wrole_lc:
                g.add((film_uri, hasCharacterWriter, w_uri))

##############################################################################
# 8) Output as RDF/XML (.owl) for Protégé
##############################################################################

output_file = "batman.owl"
g.serialize(destination=output_file, format="pretty-xml")
print(f"Successfully wrote OWL file: {output_file}")
