import scrapy
import json 
import re

class MinisterDetailsScrape(scrapy.Spider):
    name = 'minister'
    objects = []
    minister_name = ''
    position = ''
    dob = ''
    telephone = []
    party = ''
    district = ''
    overall_rank = ''
    party_rank = ''
    participation_in_parliment = ''
    related_subjects = []
    topics_participated = []
    biography = ""
    index = -1
    
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
            self.index += 1
            self.related_subjects = list(set(each_related_subjects))
            self.minister_name= response.xpath('/html/body/div[2]/section/div/div/div[2]/h1/text()').get().strip().replace("  ", " ")
            
            web_position = response.xpath('/html/body/div[2]/section/div/div/div[2]/p/text()').get()
            if web_position is not None:
                self.position=" , ".join(response.xpath('/html/body/div[2]/section/div/div/div[2]/p/text()').get().strip().split("-"))
            else:
                self.position= "පාර්ලිමේන්තු මන්ත්‍රී"
                
            self.party = response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[1]/text()[1]').get().strip().split(",")[0]
            self.district = response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[1]/a/text()').get().strip()
            self.telephone = list(set(response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[1]/text()').get().strip().split("/")))
            
        #   contact_l = []
        #   contact_l.append(response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[1]/text()').get().strip())
        #   if response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[2]/a/text()').get() is not None:
        #     contact_l.append(response.xpath('/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[2]/a/text()').get().strip())
        #   self.contact_information = contact_l

            self.overall_rank = response.xpath('/html/body/div[2]/div/div/div[1]/div[2]/div[1]/span/strong/text()').get().strip()[1:]
            self.party_rank = response.xpath('/html/body/div[2]/div/div/div[1]/div[2]/div[2]/span/strong/text()').get().strip()[1:]
            self.participation_in_parliment = response.xpath('/html/body/div[2]/div/div/div[1]/div[2]/div[3]/span/strong/text()').get().strip()
            
            # web_topics_participated_table = response.xpath('/html/body/div[2]/div/div/div[1]/div[4]')
            # web_topics_participated = web_topics_participated_table.xpath('//div/div[1]/p/a/text()').getall()
            
            # print(self.minister_name)
            # for each_topics_participated in web_topics_participated:
            #     print(each_topics_participated.strip())
            # print('\n')
            
            biography_string = ''
            birth_year = ''
            web_personal = response.xpath('/html/body/div[2]/div/div/div[1]/div[8]/table[1]/tbody/tr')
            for i in range(len(web_personal)-1,-1,-1):
                key = web_personal[i].xpath('./td[1]/text()').get().strip()
                value = web_personal[i].xpath('./td[2]/text()').get().strip()
                if key == "ස්ත්‍රී පුරුෂ භාවය:":
                    gender = value
                    if "හිමි" in self.minister_name:
                        pronoun1 = ""
                        pronoun2 = "උන්වහන්සේ "
                    if gender == "පුරුෂ" or gender == "පිරිමි" or gender == "male":
                        pronoun1 = "මහතා"
                        pronoun2 = "මෙතුමා "
                    elif gender == "ස්ත්‍රී" or gender == "ගැහැණු" or gender == "female":
                        pronoun1 = "මහත්මිය"
                        pronoun2 = "මෙතුමිය "           
                elif key == "උපන්දිනය:" and value is not None:
                    birthday = value
                    birth_year = birthday.split("-")[0]
                    birthday_string = self.minister_name + " "+ pronoun1 + " " + birthday + " " + "දින උපත ලබා ඇත." 
                    biography_string += birthday_string
            
            web_education = response.xpath('/html/body/div[2]/div/div/div[1]/div[8]/table[2]/tbody/tr')
            schools,edu_string = "",""
            for i in range(len(web_education)):
                key = web_education[i].xpath('./td[1]/text()').get()
                value = web_education[i].xpath('./td[2]/text()').get()
                if value is None:
                  continue
                else:
                  if "පාසැල" in key:
                    if edu_string == "": 
                      schools += value
                      edu_string = pronoun2 + schools + " යන පාසලේ අධ්යාපනය ලබා ඇත."
                    else:
                      schools += "; "+value+"; "
                      edu_string = pronoun2 + schools + " යන පාසල්වල අධ්යාපනය ලබා ඇත."
                  elif "ප්‍රථම උපාධිය" in key:
                    edu_string += "තම ප්‍රථම උපාධිය "+value+" ලබාගෙන ඇත."
                  elif "පශ්චාත් උපාධිය" in key:
                    edu_string += " ඊට අමතරව "+ value +" පශ්චාත් උපාධිය ද සම්පූර්ණ කර ඇත."
            biography_string += edu_string
            
            web_party = response.xpath('/html/body/div[2]/div/div/div[1]/div[8]/table[3]/tbody/tr')
            party_string,j = "",""  
            for i in range(len(web_party)):
                if i>0:
                  j = "ද"
                  if i == 1:
                    party_string+=j+" "
                duration = web_party[i].xpath('./td[1]/text()').get()
                party = web_party[i].xpath('./td[2]').get().split(">")[-2].split(",")[0].strip()
                if duration is not None and party is not None:
                  if "සිට" not in duration:
                    try:
                      start,end = duration.split(" - ")
                      party_string += start+" සිට "+end+" දක්වා "+party+j
                    except:
                      party_string += duration+" පටන්"+party+j
                  else:
                    party_string += duration+" "+party+j
            party_string += " නියෝජනය කරමින් පාර්ලිමේන්තුවේ අසුන් ගෙන සිටී."

            biography_string += party_string
            
            self.biography = biography_string
            self.dob = birth_year
            
            detail_json = {
                  'name' : self.minister_name ,
                  'position': self.position , 
                  'telephone': self.telephone,
                  'dob': self.dob,
                  'party' : self.party ,         
                  'district' : self.district ,
                  'overall_rank' : self.overall_rank ,
                  'party_rank' : self.party_rank , 
                  'participated_in_parliament' : int(self.participation_in_parliment) ,
                  'related_subjects' : self.related_subjects,
                  'biography' : self.biography
            }
            
            with open("minister_details/"+str(self.index)+".json", 'w', encoding="utf8") as outfile:
                json.dump([detail_json], outfile,indent = 4,ensure_ascii=False)
                self.objects.append(detail_json)
        
    def closed(self, reason):
            with open("all_data_json.json", 'w', encoding="utf8") as outfile:
              json.dump(self.objects, outfile,indent = 4,ensure_ascii=False)    
            
