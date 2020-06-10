if [[ $1 = "-t" ]]
then
  python3 test.py
  exit 0
fi

echo ""
echo "Welcome to Gomoku_IA"

while true
do
  echo ""
  echo "Next step, please enter the corresponding number to perform the operation."
  echo "---------------------------"
  echo "0: Exit"
  echo "1: Configure the game"
  echo "2: Run"
  echo "3: Run visual game by Web server"
  echo "4: Neural network training"
  echo "---------------------------"

  read -p ": " input
  case $input in
  0)
    break
    ;;
  1)
    python3 configure.py
    continue
    ;;
  2)
    python3 start.py
    continue
    ;;
  3)
#    export FLASK_APP=Web/__init__.py
#    export FLASK_ENV=production
#    export FLASK_DEBUG=0
#    python -m flask run --host "0.0.0.0"
    python3 start_from_web.py
    continue
    ;;
  4)
    python3 train.py
    continue
    ;;
  *)
    echo "The input is incorrect, please try again."
    continue
    ;;
  esac
done
