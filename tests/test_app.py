import time
import pytest

from app import GoodreadsAPIClient
from exceptions import InvalidGoodreadsURL, ServiceCallException

def pytest_generate_tests(metafunc):
    '''Using Parameterized , so collecting
      all the methods and params to be tested
    '''
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] \
            for funcargs in funcarglist]
    )

class TestClass:
    '''
       Test class to test different methods used in app
    '''
    '''
       As stated in the good read documentation about request should be made
       after 1 second of the previous request , so we will sleep for 2 sec
    '''   
    params = {
        "test_valid_url":[{
            "url": "https://www.goodreads.com/book/show/12177850.xml"
        },
        {
            "url": "https://www.goodreads.com/book/show/12177850.xml?a=b&c=d"
        }],
        "test_invalid_url" :[{
            "url" : "https://www.goodreads.com/book/show/12177850/sas",
        },
        {
            "url": "https://www.google.com"
        },
        {
            "url" : "https://www.goodreads.com/books/show/12177850.xml"   
        },
        {
            "url": "https://www.goodreads.com/book/shows/12177850.xml"
        },
        {
            "url": "https://www.goodreads.com/book/shows/12177850.csv"
        }],
        "test_service_caller_200OK":[{
            "url": "https://www.goodreads.com/book/show/12177850.xml"
        }],
        "test_service_caller_NOTOK":[{
            "url": "https://www.goodreads.com/book/show/1217785000000.xml"
        }],
        "test_valid_xml_parser":[{
            "url": "https://www.goodreads.com/book/show/52781202.xml"
        }],
        "test_invalid_xml_parser":[{
            "service_content": b'''
                                 <?xml version="1.0"?>
                                    <!DOCTYPE TEST
                                    <!ELEMENT TESTS (T1, T2)>
                                '''
        }],
        "test_get_book_details":[{
            "url" : "https://www.goodreads.com/book/show/52781202.xml" 
        }]
           }

    def test_valid_url(self, url):
        '''test validating valid url'''
        test_obj = GoodreadsAPIClient(url=url)
        try :
            test_obj.url_validator()
        except InvalidGoodreadsURL:
            assert False
        else :
            assert True
    
    def test_invalid_url(self, url):
        '''test invalid url'''
        test_obj = GoodreadsAPIClient(url=url)
        with pytest.raises(InvalidGoodreadsURL):
            test_obj.url_validator()
    
    def test_service_caller_200OK(self, url):
        '''test service caller method'''
        time.sleep(2)
        test_obj = GoodreadsAPIClient(url=url)
        try :
            test_obj.service_caller()
        except InvalidGoodreadsURL:
            assert False
        else :
            assert True

    def test_service_caller_NOTOK(self, url):
        '''test service caller method'''
        time.sleep(2)
        test_obj = GoodreadsAPIClient(url=url)
        with pytest.raises(ServiceCallException):
            test_obj.service_caller()
    
    def test_valid_xml_parser(self,url):
        '''test xml parser method with valid xml'''
        time.sleep(2)
        test_obj = GoodreadsAPIClient(url=url)
        try:
            test_obj.url_validator()
            test_obj.service_caller()
            test_obj.xml_parser()
        except InvalidGoodreadsURL:
            assert False
        except ServiceCallException:
            assert False
        else:
            self.assertIsInstance(test_obj._out, dict)
    
    def test_invalid_xml_parser(self,service_content):
        '''test xml parser method with invalid xml'''
        test_obj = GoodreadsAPIClient(service_content=service_content)
        test_obj.xml_parser()
        assert test_obj._out == {}
    
    def test_get_book_details(self,url):
        '''test the OG method'''
        time.sleep(2)
        test_obj = GoodreadsAPIClient()
        try :
            out_ = test_obj.get_book_details(url=url)
        except :
            assert False
        else :
            self.assertIsInstance(out_, dict)
            for key, value in out_.items():
                self.assertIsInstance(value,test_obj.out_blueprint[key])


    def assertIsInstance(self,value,datatype):
        '''assert right datatype'''
        assert isinstance(value,datatype) , 'Invalid Attr'
