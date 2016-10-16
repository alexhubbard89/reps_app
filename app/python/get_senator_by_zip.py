#Read data from stdin
def read_in():
    import sys, json, numpy as np
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def get_senator_by_zip():
    ## Find your senator by zipcode. 
    ## Because there are only two senators 
    ## and entire states are represented by
    ## those two senetors, I only need to find
    ## the state from the zip code and then
    ## locate the current senator.

    import requests
    import pandas as pd
    from pandas.io.json import json_normalize
    
    ## Get representatives from zip code.
    zip_code = read_in()


    url = 'http://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=true'.format(zip_code)
    r = requests.get(url)
    x = pd.DataFrame(json_normalize(r.json()['results']).loc[0, 'address_components']).loc[:,]
    for i in range(len(x['types'])):
        if u'administrative_area_level_1' in x.loc[i, 'types']:
    ## Save state from zipcode
            state = x.loc[i, 'short_name'].upper()

    print state



#start process
if __name__ == '__main__':
    get_senator_by_zip()