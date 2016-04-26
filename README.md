# Author-Decomposition
Our project for CSCI 544: Natural Language Processing

## Synthetic text generator
* src/ $ python3 -m synthetic_text_creator -t ../corpora/spanish_blogs2 -c 2000000 -opick continuous.pickle -oth continuous.txt

## Feature metadata generator
* src/ $ python3 -m authorclustering.feature -t ../models/spanish_blogs2/continuous/continuous.txt -word output_word.txt -char output_char.txt -pos output_pos.txt -bipos output_bipos.txt -biword output_biword.txt -triword output_triword.txt -tripos output_tripos.txt -4pos output_4pos.txt -url localhost
