import argparse
import os
from time import time

import pandas as pd
from sqlalchemy import create_engine


def ingest_callable(user, password, port, db, table_name, csv_name):
    engine = create_engine(
        f'postgresql://{user}:{password}@pgdatabase:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True,
                          chunksize=100000, sep=';')
    engine.connect()
    df = next(df_iter)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    # This is the first iteration
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            df.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print('inserted another chunk, took %.3f second' %
                  (t_end - t_start))
        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break
