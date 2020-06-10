if [[ $1 = "-t" ]]
then
  python3 test.py
  exit 0
fi

python3 start.py
python3 start_from_web.py
python3 train.py
