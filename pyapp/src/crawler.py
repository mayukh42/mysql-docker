#!/usr/bin/env python

import json, sys, requests
from models import DB_PROXY_SRC, CrawlData, create_table, custom_table_name
from utils import *


class Crawler(object):
    # args = dict of k=v
    def __init__(self, args):
        self.args = args
        self.config = get_config(self.args.get('config', './config.yaml'))
        self.logger = get_logger(self.config['log'])
        
        try:
            # db = connect_mysqldb(self.config['mysqldb'])
            db = connect_sqlitedb(self.config['sqlitedb'])
        except Exception as e:
            err_db_connect = "error in connecting to db. exiting"
            self.logger.exception(e)
            lf = get_logger_file(self.logger)
            print(f"errors occurred, see log at {lf} : {e}")
            sys.exit(1)

        self.db = DB_PROXY_SRC
        self.db.initialize(db)
    
    def create_tables(self):
        # database.create_tables([ModelA, ModelB, ...]) can be used if actual table names are known, else need to set them first
        try:
            self.db.connect()
            models = [CrawlData]
            for m in models:
                table_name = custom_table_name(m)
                create_table(m, table_name)
                self.logger.info(f"table {table_name} created")
            self.logger.info(f"created tables for {models}")
        except Exception as e:
            self.logger.exception(f"error in creating tables: {e}")
            raise e
        finally:
            self.db.close()
    
    def insert_rows(self, rows, batch_size=500):
        # rows = array of dicts
        try:
            self.db.connect()
            # TODO: refactor to dedup
            table_name = custom_table_name(CrawlData)
            # no need of self method else it would need instantiation
            CrawlData._meta.set_table_name(table_name)
            count, batch_rows = 0, []
            while len(rows) > batch_size:
                batch_rows = rows[:batch_size]
                rows = rows[batch_size:]
                CrawlData.insert_many(batch_rows).execute()
                count += len(batch_rows)
            
            # leftovers
            batch_rows = rows
            CrawlData.insert_many(batch_rows).execute()
            count += len(batch_rows)
            self.logger.info(f"inserted {count} rows")
        except Exception as e:
            self.logger.error(f"error in inserting rows: {e}")
            raise e
        finally:
            self.db.close()

    
    def crawl(self, target):
        # TODO: urlparse
        url = f"https://www.{target}"
        platform = "chrome_linux"
        uagent = uagents[platform]
        headers = {
            "user-agent": uagent
        }
        self.logger.info(f"crawling {url} as {uagent}")
        row = {}
        try:
            res = requests.get(url)
            row_dict = {
                "target": target,
                "url": url,
                "status": res.status_code,
                "encoding": res.encoding,
                "headers": res.headers,
                "responseLength": len(res.text),
            }
            self.logger.info(f"crawled {url}")
            self.logger.debug(row_dict)
            model = CrawlData()
            row = model.prepare_row(**row_dict)
        except Exception as e:
            self.logger.error(f"error in crawling to {url}: {e}")
            raise e
        return row
    
    def crawl_many(self, targets):
        # list of dicts
        rows = []
        for t in targets:
            r = self.crawl(t)
            if r:
                rows.append(r)
        self.insert_rows(rows)
        self.logger.info("crawled {} targets".format(len(targets)))


def test_setup(args):
    print(f"program args: {args}")
    config = get_config(args.get('config', './config/config.yaml'))
    print(json.dumps(config))

# convenient runner for testing
def run_crawler(args):
    c = Crawler(args)
    try:
        c.create_tables()
        targets = [
            "google.com",
            "yahoo.com",
            # "microsoft.com",
            # "xbox.com",
            "x.com",
            # "firstpost.com",
            # "duckduckgo.com",
            # "linux.com",
            # "archlinux.org",
            # "fedoraproject.org"
        ]
        c.logger.info(f"targets: {targets}")    
        c.crawl_many(targets)
    except Exception as e:        
        lf = get_logger_file(c.logger)
        print(f"errors occurred, see log at {lf} : {e}")


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    test_setup(args)
    run_crawler(args)
