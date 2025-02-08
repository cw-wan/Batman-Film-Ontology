from rdflib import Graph

# 1) Create a graph and parse an OWL file (in RDF/XML, Turtle, etc.)
g = Graph()
g.parse("batman.owl", format="xml")  # or 'ttl' if it's in Turtle

# 2) Define a SPARQL query string
sparql_query = """
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
"""

# 3) Execute the query
results = g.query(sparql_query)


# 4) Iterate over the results

def print_sparql_result_table(query_results):
    """
    Given an rdflib SPARQL query result object, print the results in
    a neat ASCII table. The columns are taken from query_results.vars,
    and each row is built from the returned bindings.
    """
    # 1) Gather variable names (header row)
    var_names = list(query_results.vars)  # e.g., ['filmTitle', 'year', ...]

    # We'll store rows as a list of lists (including header as first row).
    rows = [var_names]

    # 2) Collect the data rows
    for row in query_results:
        row_cells = []
        for var in var_names:
            val = row[var]  # rdflib Term (Literal, URIRef, etc.) or None
            if val is None:
                row_cells.append("")
            else:
                # Convert to string. If you need more specialized formatting
                # (e.g., showing ^^xsd:string), you can adjust here.
                row_cells.append(str(val))
        rows.append(row_cells)

    # 3) Compute column widths
    # First, we need the number of columns.
    num_cols = len(var_names)
    col_widths = [0] * num_cols
    for row_vals in rows:
        for i, cell in enumerate(row_vals):
            col_widths[i] = max(col_widths[i], len(cell))

    # 4) Helper to print a divider line
    def print_divider(char="-"):
        # total width = sum of col_widths plus 3 chars per column (space + "|")
        # We'll do something like:  "| col1 | col2 | ... "
        total_width = sum(col_widths) + (3 * num_cols) + 1
        print(char * total_width)

    # 5) Print the table
    # Print top divider
    print_divider("-")

    # Print header row
    header_cells = rows[0]
    header_str = ""
    for i, cell in enumerate(header_cells):
        header_str += f"| {cell.ljust(col_widths[i])} "
    header_str += "|"
    print(header_str)

    # Print a separator using '='
    print_divider("=")

    # Print data rows
    for data_row in rows[1:]:
        row_str = ""
        for i, cell in enumerate(data_row):
            row_str += f"| {cell.ljust(col_widths[i])} "
        row_str += "|"
        print(row_str)

    # Print bottom divider
    print_divider("-")


print_sparql_result_table(results)
