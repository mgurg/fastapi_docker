DIR="$( cd "$( dirname "$0" )" && pwd )"

echo "export requirements.txt"
poetry export -o requirements.txt --without-hashes
poetry export -o requirements-dev.txt --dev --without-hashes
echo "autoflake APP"
autoflake --recursive --in-place  \
        --remove-unused-variables \
        --remove-all-unused-imports  \
        --ignore-init-module-imports \
        app
echo "autoflake TESTS"
autoflake --recursive --in-place  \
        --remove-unused-variables \
        --remove-all-unused-imports  \
        --ignore-init-module-imports \
        tests        
echo "black"
black --line-length 120 app
black --line-length 120 tests
echo "isort"
isort app
# echo "flake8"
# flake8 app --count --statistics --max-line-length 120
echo "ruff"
ruff app --line-length=120
echo "truncate log file"
: > $DIR/app/logs/logs.log
echo "OK"
