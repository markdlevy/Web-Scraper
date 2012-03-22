
'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib2
import lxml.etree
import lxml.html
import csv
import re

appid = input('Please enter your API key or app ID: ')
rec = 1

doc = lxml.etree.parse(urllib2.urlopen("http://www.charitynavigator.org/feeds/search4/?appid=%d&fromrec=%d" % (appid, rec)))
 
maxrec = int(doc.getroot().get('total'))

results = []

for rec in range(1, maxrec, 25):
    # print "Downloading dataset %d out of %d" % ((1+rec/25),maxrec/25)
    doc = lxml.etree.parse(urllib2.urlopen("http://www.charitynavigator.org/feeds/search4/?appid=%d&fromrec=%d" % (appid, rec)))
    for charity in doc.findall('charity'):
        try:
            results.append(dict((item.tag, item.text.encode('utf-8')) for item in charity.iterchildren()))
        except:
            # print "Exception (probably utf-8 encoder)"
            results.append(dict((item.tag, item.text) for item in charity.iterchildren()))
    # with open('xml/%05d.xml' % rec,'wb') as f:
    #       f.write(data.read()) # save a copy, just in case

for i, charity in enumerate(results):
    doc = lxml.html.parse(urllib2.urlopen(charity['url'],timeout=6000))
#    print "Processing charity %s out of %s, id: %s" % (i, len(results), charity['orgid'])
    def rating(path):
        """ Take xpath to tabular data and clean it up by removing paretheses.
        """
        return doc.xpath(path)[0].text.replace('(','').replace(')','').encode('utf-8')
    def percent(path):
        """ Take xpath to tabular data and clean it up by removing % sign and spaces.
        """
        return doc.xpath(path)[0].text.replace('%','').replace(' ','').encode('utf-8')
    def dollar(path):
        """ Take xpath to tabular data and clean it up by removing $ sign.
        """
        return doc.xpath(path)[0].text.replace('$','').replace(',','').encode('utf-8')

    ## EIN (Federal ID)
    charity['ein'] = re.search("\d{2}-\d{7}",doc.xpath("/html/body/div[@id='wrapper']/div[@id='wrapper2']/div[@id='bodywrap']/div[@id='cn_body']/div[@id='cn_body_inner']/div[@id='leftcontent']/div[@id='leftnavcontent']/div[1][@class='rating']/p[1]/a")[0].tail).group().encode('utf-8')
    ## Overall Rating (Out of 70)
    charity['overall_rating'] = rating("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[2]/td[4]")
    ## Efficiency Rating (Out of 40)
    charity['efficiency_rating'] = rating("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[9]/td[4]")
    ## Capactiy Rating (Out of 30)
    charity['capacity_rating'] = rating("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[15]/td[4]")
    ## Overall Rating (Stars)
    try:
        charity['overall_rating_star'] = re.match('\d',doc.xpath("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[1]/td[4]/img")[0].get('alt')).group().encode('utf-8')
    except:
        charity['overall_rating_star'] = 0
    ## Efficiency Rating (Stars)
    try:
        charity['efficiency_rating_star'] = re.match('\d',doc.xpath("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[8]/td[4]/img")[0].get('alt')).group().encode('utf-8')
    except:
        charity['efficiency_rating_star'] = 0
    ## Capacity Rating (Stars)
    try:
        charity['capacity_rating_star'] = re.match('\d',doc.xpath("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[14]/td[4]/img")[0].get('alt')).group().encode('utf-8')
    except:
        charity['capacity_rating_star'] = 0
    ## Program Expenses (as a percentage of TFE)
    charity['program_expense_percent'] = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[4]/td[2]")
    ## Administrative Expenses (as a percentage of TFE)
    charity['admin_expense_percent'] = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[5]/td[2]")
    ## Fundraising Expenses  (as a percentage of TFE)
    charity['fund_expense_percent'] = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[6]/td[2]")
    ## Fundraising Efficiency
    charity['fund_efficiency'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[7]/td[2]")
    ## Primary Revenue Growth
    charity['primary_revenue_growth'] = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[11]/td[2]")
    ## Program Expense Growth
    charity['program_expense_growth'] = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[12]/td[2]")
    ## Working Capital Ratio (Years)
    charity['working_capital_ratio'] = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[1]/div[@class='rating']/table/tr[13]/td[2]")
    ## Primary Revenue
    charity['primary_revenue'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[2]/td[2]")
    ## Other Revenue
    charity['other_revenue'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[3]/td[2]")
    ## Total Revenue
    charity['total_revenue'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[4]/td[2]/strong")
    ## Program Expenses (absolute)
    charity['program_expense'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[7]/td[2]")
    ## Administrative Expenses
    charity['admin_expense'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[8]/td[2]")
    ## Fundraising Expenses (absolute)
    charity['fund_expense'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[9]/td[2]")
    ## Total Functional Expenses
    charity['total_functional_expense'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[10]/td[2]/strong")
    ## Payments to Affiliates
    charity['affiliate_payments'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[12]/td[2]")
    ## Budget Surplus
    charity['budget_surplus'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[13]/td[2]")
    ## Net Assets
    charity['net_assets'] = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[1][@class='leftcolumn']/div[2]/div[@class='rating']/table/tr[15]/td[2]")
    ## Leadership Compensation
    comp = dollar("//div[@id='summary']/div[2][@class='summarywrap']/div[3][@class='bottom']/div[2][@class='leadership']/table/tr[2]/td[3][@class='rightalign']")
    if comp.strip() == 'Not compensated':
        charity['leader_comp'] = 0
    elif comp.strip() == 'None reported':
        charity['leader_comp'] = ''
    else:
        charity['leader_comp'] = comp
    ## Leadership Compensation as % of Expenses
    cp = percent("//div[@id='summary']/div[2][@class='summarywrap']/div[3][@class='bottom']/div[2][@class='leadership']/table/tr[2]/td[4][@class='rightalign']")
    if comp.strip() == 'Not compensated':
        charity['leader_comp_percent'] = 0
    elif comp.strip() == 'None reported':
        charity['leader_comp_percent'] = ''
    else:
        charity['leader_comp_percent'] = cp
    ## Website and E-mail
    for link in doc.xpath("//div[@id='leftnavcontent']/div[1][@class='rating']/p[2]/a"):
        if link.text == 'Visit Web Site':
            charity['website'] = link.get('href').encode('utf-8')
        if link.text == 'Contact Email':
            charity['email'] = link.get('href').replace('mailto:','').encode('utf-8')

with open('output.csv','wb') as f:
    all_fields = results[0].keys()
    ordered_fields = "orgid ein charity_name category city state".split()
    unordered_fields = list(set(all_fields) - set(ordered_fields))
    fn = ordered_fields
    fn.extend(unordered_fields)
    writer=csv.DictWriter(f, fieldnames=fn, extrasaction='ignore')
    headers={}
    for n in fn:
        headers[n]=n
    writer.writerow(headers)
    for charity in results:
        writer.writerow(charity)