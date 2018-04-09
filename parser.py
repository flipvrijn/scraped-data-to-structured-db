import json
import os.path
from io import StringIO

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from stores import *
import models
from models import get_or_create


def save_to_db(db_file, store):
    engine = create_engine('sqlite:///{}'.format(db_file))
    Session = sessionmaker(bind=engine)

    # Initialize DB if needed
    if not os.path.isfile(db_file):
        models.Base.metadata.create_all(engine)

    # Save to database
    session  = Session()

    # Select/save store
    db_store = get_or_create(session, models.Store, name=store.name)
    store_id = db_store.id

    # Process the gathered data
    for overview_page in tqdm(store.overview_pages):
        # Save category hierarchy
        category_parent_id = None
        for category in overview_page['product_category']:
            # Check if exists...
            res = session.query(models.Category).filter(models.Category.name == category).filter(models.Category.parent_id == category_parent_id).first()
            # ... else create new category
            if res:
                category_parent_id = res.id
            else:
                new_category = models.Category(name=category, parent_id=category_parent_id)
                session.add(new_category)
                session.commit()
                category_parent_id = new_category.id

        # Save products
        for position, product_url in enumerate(overview_page['product_urls']):
            if product_url in store.product_pages.keys():
                product = store.product_pages[product_url]

                # Select/save brand
                db_brand = get_or_create(session, models.Brand, name=product['brand'])
                brand_id = db_brand.id

                # Save product
                new_product = models.Product(
                    name=product['product_name'],
                    type=product['product_type'],
                    price=product['price'],
                    page_position=position + 1,                 # From 0-based to 1-based
                    page_number=overview_page['page_number'],
                    category_id=category_parent_id,
                    brand_id=brand_id,
                    store_id=store_id
                )
                session.add(new_product)
                session.commit()
    session.close()

def main():
    db_file = 'store.db'
    
    # Read files
    input_files = {
        'data/crawl_omoda.nl_2016-05-30T23-14-58.jl': Omoda(),
        'data/crawl_ziengs.nl_2016-05-30T23-15-20.jl': Ziengs(),
        'data/crawl_zalando.nl_2016-05-30T23-14-36.jl': Zalando(),
    }

    for f_in, store in input_files.iteritems():
        # Process products 
        with open(f_in, 'r') as f_in:
            for i, line in tqdm(enumerate(f_in)):
                json_obj = json.load(StringIO(unicode(line.encode('utf-8'))))
                store.parse(json_obj)

        save_to_db(db_file, store)        

if __name__ == '__main__':
    main()