echo "export requirements.txt"
poetry export -o requirements.txt --without-hashes
poetry export -o requirements-dev.txt --dev --without-hashes
echo "autoflake"
autoflake --recursive --in-place  \
        --remove-unused-variables \
        --remove-all-unused-imports  \
        --ignore-init-module-imports \
        app
echo "black"
black --line-length 120 app
echo "isort"
isort app
echo "flake8"
flake8 app --count --statistics --max-line-length 120
echo "OK"
