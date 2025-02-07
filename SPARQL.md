
Get all the Batman films released before 2000.
```sparksql
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
```sparksql
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
