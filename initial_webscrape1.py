import requests
import lxml.html as lh
import pandas as pd

url='https://nextgenstats.nfl.com/stats/passing/2020/REG/1#yards'
#Create a handle, page, to handle the contents of the website
page = requests.get(url)
#Store the contents of the website under doc
doc = lh.fromstring(page.content)
#Parse data that are stored between <tr>..</tr> of HTML

table = doc.xpath('//div[class="ngs-data-table"]/text()')
print(table)
