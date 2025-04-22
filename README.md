loogle-aeneas
=============

This is a fork of Loogle, adapted to search through the Aeneas library in
addition to the Mathlib library. It is meant to be run locally.

Usage
-----

Build the search index with `make`, then run the server by running the `server.py` file
(e.g., `python3 server.py`). This will allow you to open Loogle in your browser.

Whenever you want to update the search index following changes in Aeneas, simply
pull the latest version of `loogle-aeneas` and rebuild the index with `make`.

Aknowledgements
---------------
This fork was adapted thanks to the precious help of Joachim Breitner.
