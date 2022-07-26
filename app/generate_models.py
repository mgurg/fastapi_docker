import io
import sys

from sqlacodegen.generators import CodeGenerator
from sqlalchemy import MetaData, create_engine


def generate_model(host, user, password, database, outfile=None):
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")
    metadata = MetaData(bind=engine)
    metadata.reflect()
    outfile = io.open(outfile, "w", encoding="utf-8") if outfile else sys.stdout
    generator = CodeGenerator(metadata)
    generator.render(outfile)


if __name__ == "__main__":
    generate_model("database.example.org", "dbuser", "secretpassword", "mydatabase", "db.py")
