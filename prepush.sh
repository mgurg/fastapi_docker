DIR="$( cd "$( dirname "$0" )" && pwd )"

echo "export requirements.txt"
poetry export -o requirements.txt --without-hashes
poetry export -o requirements-dev.txt --with dev --without-hashes

echo "ruff"
ruff app --fix
ruff migrations/versions/ --fix
ruff format app
ruff format migrations
echo "truncate log file"
: > $DIR/app/logs/logs.log
echo "OK"
