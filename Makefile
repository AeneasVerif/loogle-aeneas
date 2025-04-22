all: index.olean

index.olean:
	lake build LoogleMathlibCache
	lake exec loogle --module Aeneas --write-index index.olean
