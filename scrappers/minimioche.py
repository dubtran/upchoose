import boto3
from bs4 import BeautifulSoup
import requests as req
import json
import opengraph
import time
import json

minimioche_url = 'http://www.minimioche.com'

def getColors(product_url):
    ''' parses colors from the color tool tip'''

    html = req.get(product_url)
    soup = BeautifulSoup(html.content, 'lxml')
    
    colorbar = soup.find_all('div', class_ = 'tooltip')
    color = [c.text.encode('utf-8') for c in colorbar]
    return color

def getProductInfo(product_url):
    '''gathering data from Open Graph'''

    prod_url = minimioche_url+product_url
#     print prod_url
    prod_site =  opengraph.OpenGraph(url=prod_url)
#     product_data = dict.fromkeys(product_keys)
    if prod_site.is_valid(): 
        product_data = json.loads(prod_site.to_json().encode('utf-8'))
        product_data['colors'] = getColors(prod_url)
        return product_data
    else:
        print prod_url, ' didnt work '
        return 'na'

def getCollection(collection_soup):
    ''' iterating through an individual collection'''

    collection = []
    for x in collection_soup.find_all('figure', class_ = 'card grid-3'):
    #     getProductInfo(x['href'])p
        collection.append(getProductInfo(x.a['href']))
        time.sleep(2)
    return collection

def sendToS3(json_collection, collection):
    s3_bucket = 'upchoose-data'
    s3_path = ('minimioche/%s/20161125.json' % collection)
    s3 = boto3.client('s3')
    with open(('%s_20161125.json' % collection), 'w') as outfile:
        json.dump(json_collection, outfile)
        s3.upload_fileobj(outfile, s3_bucket, s3_path)
        # check if file got uploaded 

# TODO TRANSFER SQL


def main():
    clothing = ['tops','bottoms','onesies','dresses','rompers','sleepwear','outerwear','swim','footwear']
    for c in clothing:
     
        m = req.get(( 'http://www.minimioche.com/collections/%s' % c))
        soup = BeautifulSoup(m.content, 'lxml')
        clothes = getCollection(soup)
        sendToS3(clothes, c)
        to_df = gatherSqlData(clothes, c)

if __name__ == '__main__':
    main()