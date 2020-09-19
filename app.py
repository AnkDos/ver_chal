import requests
import logging

from decouple import config
from lxml import etree as et
from urllib.parse import urlparse,urljoin

from exceptions import InvalidGoodreadsURL, ServiceCallException

class GoodreadsAPIClient:
    '''Main Class'''
    def __init__(self,url=None,service_content=None):
        ''''''
        self.out_blueprint = {
          "title": str ,
          "average_rating": float ,
          "ratings_count": int ,
          "num_pages": int ,
          "image_url": str ,
          "publication_year": int,
          "authors": str
        }
        self._out = {}
        self.url = url
        self.service_content = service_content
    
    def url_validator(self):
        '''validating input url'''
        if not self.url:
            raise InvalidGoodreadsURL('''Invalid URL Format, please follow 
                                       API URL FORMAT as stated in doc''')

        urlparse_obj = urlparse(self.url)
        try :
            path = list(filter(None, urlparse_obj.path.split('/')))
            assert urlparse_obj.scheme == 'https'
            assert urlparse_obj.netloc == 'www.goodreads.com' 
            assert len(path) == 3
            assert path[0] == 'book'
            assert path[1] == 'show'
            sub_paths = path[-1].split('.')
            sub_paths[0] = int(sub_paths[0])
            assert sub_paths[-1] == 'xml'
            assert isinstance(sub_paths[0],int)
            assert sub_paths[0] >= 0
        except AssertionError:
            raise InvalidGoodreadsURL('''Invalid URL Format, please follow 
                                       API URL FORMAT as stated in doc''')
        except IndexError:
            raise InvalidGoodreadsURL('''Invalid URL Format, please follow
                                        API URL FORMAT as stated in doc''')
        except ValueError:
            raise InvalidGoodreadsURL('''Invalid URL Format, please follow
                                       API URL FORMAT  as stated in doc''')
        else :
            self.url = urljoin(self.url, urlparse(self.url).path)


    def service_caller(self):
        '''Calling goodreads service'''
        params = {
            'format': 'xml',
            'key' : config('SECRET_KEY')
        }
        response = requests.get(url=self.url, params=params)
        if response.status_code != 200:
            raise ServiceCallException("Error While Retriving The Data")
        self.service_content = response.content
    
    def xml_parser(self):
        '''parsing the xml response'''
        authors = []
        try :
            xml_content = et.fromstring(self.service_content)
        except et.XMLSyntaxError:
            return 

        for elements in xml_content.getchildren():
            for sub_elements in elements.getchildren():
                if sub_elements.tag in self.out_blueprint:
                    if sub_elements.tag == 'authors':
                        for author in sub_elements.iter():
                            if author.tag == 'name':
                                authors.append(author.text)
                        if authors:
                            self._out[sub_elements.tag] =\
                             self.out_blueprint[sub_elements.tag]\
                                 (','.join(authors))
                        continue
                    if sub_elements.text:
                        self._out[sub_elements.tag] =\
                         self.out_blueprint[sub_elements.tag]\
                             (sub_elements.text)
        
    def get_book_details(self,url):
        '''A method for all methods'''
        self.url = url
        self.url_validator()
        self.service_caller()
        self.xml_parser()
        return self._out


if __name__ == '__main__':
    url = str(input()).strip()
    try:
        api_caller = GoodreadsAPIClient()
        out = api_caller.get_book_details(url=url)
    except Exception as exp:
        logging.exception('Exception %s', exp)
    else:
        print(out)
