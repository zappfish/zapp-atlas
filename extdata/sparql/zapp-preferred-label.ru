# Use each term's ZAPP preferred label as its rdfs:label.
#
# ZP marks the label ZAPP wants shown as an exact synonym whose axiom carries
# OMO:0002001 ("preferred label for") -> the ZAPP information resource. Swap
# it in, and keep the ontology's own label as an exact synonym so a search for
# it still finds the term.
#
# TEMPORARY: some terms currently carry two ZAPP preferred labels (an
# upstream bug). Until that is fixed, the alphabetically first one wins.

PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

DELETE {
  ?term rdfs:label ?label .
  ?term oboInOwl:hasExactSynonym ?preferred .
  ?axiom ?p ?o .
}
INSERT {
  ?term rdfs:label ?preferred .
  ?term oboInOwl:hasExactSynonym ?label .
}
WHERE {
  {
    SELECT ?term (MIN(STR(?candidate)) AS ?chosen)
    WHERE {
      ?candidateAxiom owl:annotatedSource ?term ;
        owl:annotatedProperty oboInOwl:hasExactSynonym ;
        owl:annotatedTarget ?candidate ;
        obo:OMO_0002001 <https://w3id.org/information-resource-registry/zapp> .
    }
    GROUP BY ?term
  }
  ?axiom owl:annotatedSource ?term ;
    owl:annotatedProperty oboInOwl:hasExactSynonym ;
    owl:annotatedTarget ?preferred ;
    obo:OMO_0002001 <https://w3id.org/information-resource-registry/zapp> ;
    ?p ?o .
  FILTER(STR(?preferred) = ?chosen)
  ?term rdfs:label ?label .
}
