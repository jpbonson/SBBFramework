# sh appender.sh 0
cat hands5000/hands_type_$1.json hands10000/hands_type_$1.json  hands15000/hands_type_$1.json hands20000/hands_type_$1.json hands25000/hands_type_$1.json hands30000/hands_type_$1.json hands35000/hands_type_$1.json hands40000/hands_type_$1.json hands45000/hands_type_$1.json hands50000/hands_type_$1.json >> hands_type_$1.json

# cat *.json > hands_type_all.json