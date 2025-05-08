all: index.olean

index.olean: lake-manifest.json
	lake build LoogleMathlibCache
	lake exec loogle --module Aeneas --write-index index.olean
