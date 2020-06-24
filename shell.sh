#!/bin/bash

> out.txt

# sum = 0
for i in {1..20}
do
	# echo "Being ran 100 times:"
	python finalproject.py 5 1 1;
	# var=$(python calvinlast.py 0 1 1)
	# if [ "var" == "Success!" ]
	# then
	# 	sum=$((sum++))
	# fi
done

# sum=$((sum/3))
# echo "Number of Successes: $sum"
# echo "Sucess Rate: $sum"
