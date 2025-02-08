# Batman Film KG

## SPARQL

Get all the Batman films released before 2000.
```sparql
PREFIX ns: <http://www.semanticweb.org/charleswan/ontologies/batman-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX tg:<http://www.turnguard.com/functions#>

SELECT ?filmTitle ?year
WHERE {
    ?film rdf:type ns:Film .
    ?film ns:hasTitle ?filmTitle .
    ?film ns:hasReleaseDate ?date .
    ?date ns:hasYear ?year.
    FILTER(?year < 2000) .
}
```
Result:
```text
---------------------------------------
| filmTitle                    | year |
=======================================
| Batman: Mask of the Phantasm | 1993 |
| Batman                       | 1989 |
| Batman Forever               | 1995 |
| Batman & Robin               | 1997 |
| Batman & Mr. Freeze: SubZero | 1998 |
| Batman Returns               | 1992 |
---------------------------------------
```

Rank all the directors based on their average IMDB ratings of their films.
```sparql
PREFIX ns: <http://www.semanticweb.org/charleswan/ontologies/batman-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX tg:<http://www.turnguard.com/functions#>

SELECT ?directorName (AVG(?rating) AS ?averageRating)
WHERE {
  ?film rdf:type ns:Film .
  ?film ns:hasImdbRating ?rating .
  ?film ns:hasDirector ?director .
  ?director rdf:type ns:Director .
  ?director ns:name ?directorName .
}
GROUP BY ?directorName
ORDER BY DESC(?averageRating)
```
Result:
```text
-----------------------------------------
| directorName      | averageRating     |
=========================================
| Christopher Nolan | 8.533333333333333 |
| Brandon Vietti    | 8.0               |
| Jay Oliva         | 7.966666666666666 |
| Eric Radomski     | 7.8               |
| Bruce Timm        | 7.8               |
| Kevin Altieri     | 7.8               |
| Frank Paur        | 7.8               |
| Dan Riba          | 7.8               |
| Curt Geda         | 7.8               |
| Boyd Kirkland     | 7.5               |
| Ethan Spaulding   | 7.5               |
| Lauren Montgomery | 7.4               |
| Tim Burton        | 7.25              |
| Sam Liu           | 6.833333333333333 |
| Zack Snyder       | 6.45              |
| Joel Schumacher   | 4.550000000000001 |
-----------------------------------------
```

Get all the directors who have experience in script writing (any contribution among story, screenplay and characters):
```sparql
PREFIX ns: <http://www.semanticweb.org/charleswan/ontologies/batman-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX tg:<http://www.turnguard.com/functions#>

SELECT DISTINCT ?directorName
WHERE {
    ?dir rdf:type ns:Director .
    ?dir ns:name ?directorName .
    {
        ?f ns:hasStoryWriter ?dir
    }
    UNION
    {
        ?f ns:hasScreenplayWriter ?dir
    }
    UNION
    {
        ?f ns:hasCharacterWriter ?dir
    }
}
```

## Rule-based Inference

Define rules:
```text
@prefix ns: <http://www.semanticweb.org/charleswan/ontologies/batman-ontology#>.
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

[rule1: (?FA rdf:type ns:Film) (?FB rdf:type ns:Film) (?FA ns:hasDirector ?DA) (?FB ns:hasDirector ?DA) (?FA ns:hasReleaseDate ?TA) (?FB ns:hasReleaseDate ?TB) (?TA ns:hasYear ?YA) (?TB ns:hasYear ?YB) greaterThan(?YB, ?YA) -> (?FA ns:hasSequel ?FB)]
[rule2: (?FA rdf:type ns:Film) (?FB rdf:type ns:Film) (?FA ns:hasSequel ?FB) -> (?FB ns:hasPrequel ?FA)]
```

Find all prequel-sequel pairs that the sequel achieves a better rating than the prequel:
```sparql
PREFIX ns: <http://www.semanticweb.org/charleswan/ontologies/batman-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX tg:<http://www.turnguard.com/functions#>

SELECT ?prequel ?yearPrequel ?ratingPrequel ?sequel ?yearSequel ?ratingSequel
WHERE {
    ?filmA rdf:type ns:Film .
    ?filmB rdf:type ns:Film .
    ?filmA ns:hasSequel ?filmB .
    ?filmA ns:hasTitle ?prequel .
    ?filmB ns:hasTitle ?sequel .
    ?filmA ns:hasReleaseDate ?dA .
    ?filmB ns:hasReleaseDate ?dB .
    ?dA ns:hasYear ?yearPrequel .
    ?dB ns:hasYear ?yearSequel .
    ?filmA ns:hasImdbRating ?ratingPrequel .
    ?filmB ns:hasImdbRating ?ratingSequel .
    FILTER (?ratingPrequel < ?ratingSequel) .
}
```
Result:
```text
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
| prequel                                               | yearPrequel | ratingPrequel    | sequel                                                | yearSequel | ratingSequel     |
==================================================================================================================================================================================
| "Batman Begins"^^xsd:string                           | 2005        | "8.2"^^xsd:float | "The Dark Knight Rises"^^xsd:string                   | 2012       | "8.4"^^xsd:float |
| "Batman Begins"^^xsd:string                           | 2005        | "8.2"^^xsd:float | "The Dark Knight"^^xsd:string                         | 2008       | "9.0"^^xsd:float |
| "Batman: The Dark Knight Returns, Part 1"^^xsd:string | 2012        | "8.0"^^xsd:float | "Batman: The Dark Knight Returns, Part 2"^^xsd:string | 2013       | "8.4"^^xsd:float |
| "Batman: The Killing Joke"^^xsd:string                | 2016        | "6.4"^^xsd:float | "Batman: Gotham by Gaslight"^^xsd:string              | 2018       | "6.7"^^xsd:float |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

Use hasPrequel in query to get the same result:
```sparql
PREFIX ns: <http://www.semanticweb.org/charleswan/ontologies/batman-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX tg:<http://www.turnguard.com/functions#>

SELECT ?prequel ?yearPrequel ?ratingPrequel ?sequel ?yearSequel ?ratingSequel
WHERE {
	?filmA rdf:type ns:Film .
	?filmB rdf:type ns:Film .
	?filmA ns:hasPrequel ?filmB .
	?filmA ns:hasTitle ?sequel .
	?filmB ns:hasTitle ?prequel .
	?filmA ns:hasReleaseDate ?dA .
	?filmB ns:hasReleaseDate ?dB .
	?dA ns:hasYear ?yearSequel .
	?dB ns:hasYear ?yearPrequel .
	?filmA ns:hasImdbRating ?ratingSequel .
	?filmB ns:hasImdbRating ?ratingPrequel .
	FILTER (?ratingPrequel < ?ratingSequel) .
}
```

