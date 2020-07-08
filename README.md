# COMP3009J Information Retrieval
##What kind of corpus it can run?
Both large and small. For the first time, large is around 2 min, small is around 3 seconds.




##What can it do?
python search.py -m manual > -- input the query and output a list of documents with rank of BM25
python search.py -m evaluation >-- print the average evaluation score of all documents




##What files inside?
index.txt,index1.txt,index2.txt is for the system reuse the past dictionaries
output.txt is retrived documents for each query
index.txt>--all terms and their frequencies of all queries
index1.txt>--idfs
index2.txt>--lengths for all documents