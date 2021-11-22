import scrapy
import json 
import re

class DetailsScrape(scrapy.Spider):
    name = 'details'
    objects = []
    minister_name = ''
    all_minister_names = []
    district = ''
    all_districts = []
    email = ''
    all_emails = []
    party = ''
    all_parties = []
    position = ''
    all_positions = []
    related_subjects = []
    all_related_subjects = []
    
    allowed_domains= [
        'manthri.lk'
        ]
        
    def start_requests(self):
        urls = [
            "http://www.manthri.lk/si/politicians",
        ]
        base_url = "http://www.manthri.lk/si/politicians?page="
        for i in range(2,10):
            urls.append(base_url+str(i))
    
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            print(url)
    
    def parse(self, response):
        web_page_names = response.xpath('/html/body/div[2]/div/div[1]/ul[1]/li/h4/a/@href').getall()
        for each_name in web_page_names:
            each_name = "http://www.manthri.lk/"+each_name
            each_related_subjects = []
            yield scrapy.Request(each_name, callback=self.details_scraper,cb_kwargs=dict(each_related_subjects = each_related_subjects))
        
    def details_scraper(self,response,each_related_subjects):
        table = response.xpath('/html/body/div[2]/div/div/div[1]/div[6]/table')
        if(len(table)==0):
            each_related_subjects = []
            load_more_button = None
        else:
            table_details = response.xpath('/html/body/div[2]/div/div/div[1]/div[6]/table')[0]
            all_related_subjects = table_details.xpath('//tbody/tr/td[3]/ul/li/a/text()').getall()
            for each_subject in all_related_subjects:
                each_related_subjects.append(each_subject.strip())
            load_more_button = response.xpath('/html/body/div[2]/div/div/div[1]/div[6]/div/a/@href').get()
            #print(load_more_button)
        if(load_more_button is not None):
            load_more_button =  "http://www.manthri.lk/" + load_more_button
            yield scrapy.Request(load_more_button, callback=self.details_scraper,cb_kwargs=dict(each_related_subjects = each_related_subjects)) #expand table and scraping all the related subjects from there
        else:
            self.related_subjects = list(set(each_related_subjects))
            self.minister_name= response.xpath('/html/body/div[2]/section/div/div/div[2]/h1/text()').get().strip().replace("  ", " ")
            
            web_position = response.xpath('/html/body/div[2]/section/div/div/div[2]/p/text()').get()
            if web_position is not None:
                self.position=" , ".join(response.xpath('/html/body/div[2]/section/div/div/div[2]/p/text()').get().strip().split("-"))
            else:
                self.position= "පාර්ලිමේන්තු මන්ත්‍රී"
                
            self.party = response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[1]/text()[1]').get().strip().split(",")[0]
            self.district = response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[1]/a/text()').get().strip()
            self.email = response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[2]/a/text()').get().strip()
         
            self.all_minister_names.append(self.minister_name)
            self.all_districts.append(self.district)
            self.all_emails.append(self.email)
            self.all_parties .append(self.party)
            self.all_positions.append(self.position)
            self.all_related_subjects += self.related_subjects
            
        
    def closed(self, reason):
        self.all_minister_names = list(set(self.all_minister_names))
        self.all_districts = list(set(self.all_districts))
        self.all_emails = list(set(self.all_emails))
        self.all_parties = list(set(self.all_parties))
        self.all_positions = list(set([ p.split(",")[0] for p in self.all_positions]))
        self.all_related_subjects = list(set(self.all_related_subjects))
        
        self.objects = {
          "names" : self.all_minister_names,
          "districts" : self.all_districts,
          "emails": self.all_emails,
          "parties" : self.all_parties,
          "positions" : self.all_positions,
          "realated_sub" : self.all_related_subjects
        }
        
        with open("details.json", 'w', encoding="utf8") as outfile:
             json.dump(self.objects, outfile,indent = 4,ensure_ascii=False)    
            
