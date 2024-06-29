from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class PostData:
    author_first_name: str
    author_last_name: str
    author_title: str
    post_content: str
    like_count: str
    comment_count: str
    publish_date: str
    member_id: str
    page_lang: str

class htmlParser:
    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as config_file:
            self.html_separators = json.load(config_file)

    def extract_author_name(self, soup):
        try:
            author_fullname = soup.find('a', class_=self.html_separators["author_fullname_separator"])
            if author_fullname:
                author_name = author_fullname.text.strip()
                author_name_parts = author_name.split()
                if len(author_name_parts) == 1:
                    author_first_name = author_name_parts[0]
                    author_last_name = ""
                elif len(author_name_parts) == 2:
                    author_first_name, author_last_name = author_name_parts
                else:
                    author_first_name = " ".join(author_name_parts[:-1])
                    author_last_name = author_name_parts[-1]
            else:
                author_first_name = author_last_name = ""
        except Exception as e:
            print("An error occured while extracting author's name/surname: ", e)
            author_first_name = author_last_name = ""
        return {
            "First name of the author is: ": author_first_name,
            "Last name of the author is: ": author_last_name
        }

    def extract_author_title(self, soup):
        try:
            author_title_link = soup.find('p', class_=self.html_separators["author_title_link_separator"])
            author_title = author_title_link.text.strip() if author_title_link else ""
        except Exception as e:
            print("An error occured while extracting author's title: ", e)
            author_title = ""
        return{
            "The title of the author is: ": author_title
        }

    def extract_post_content(self, soup):
        try:
            post_content = soup.find('p', class_=self.html_separators["post_content_separator"])
            content = post_content.text.strip() if post_content else ""
        except Exception as e:
            print("An error occured while extracting content of the post: ", e)
            content = ""
        return{
            "Content of the post: ": content
        }

    def extract_like_count(self, soup):
        try:
            like = soup.find('div', class_=self.html_separators["like_separator"])
            like_count = like.find('span', class_=self.html_separators["like_count_separator"]).text.strip() if like else "0"
        except Exception as e:
            print("An error occured while extracting number of likes: ", e)
            like_count = "0"
        return{
            "Number of likes: ": like_count
        }

    def extract_comment_count(self, soup):
        try:
            comment = soup.find('div', class_=self.html_separators["comment_separator"])
            comment_count = comment.find('a', class_=self.html_separators["comment_count_separator"]).text.strip() if comment else "0"
            split_comment = comment_count.split()
            comment_count = split_comment[0]
        except Exception as e:
            print("An error occured while extracting number of comments: ", e)
            comment_count = "0"
        return{
            "Number of comments: ": comment_count
        }

    def extract_publish_date(self, soup):
        try:
            publish_date_link = soup.find('time', class_=self.html_separators["publish_date_separator"])
            publish_date_text = publish_date_link.text.strip() if publish_date_link else ""
            if publish_date_text:
                interval = int(publish_date_text[:-1])
                unit = publish_date_text[-1]
                unit_map = {'d': 'days', 'w': 'weeks', 'm': 'months', 'y': 'years'}
                time_delta = timedelta(**{unit_map[unit]: interval})
                publish_date = datetime.now() - time_delta
                formatted_publish_date = publish_date.isoformat()
            else:
                formatted_publish_date = ""
        except Exception as e:
            print("An error occurred while extracting date of publishing: ", e)
            formatted_publish_date = ""
        return {
            "The date of publishing is: ": formatted_publish_date
        }

    def extract_member_id(self, soup):
        try:
            member_id_link = soup.find('a', class_=self.html_separators["member_id_separator"])
            if member_id_link:
                member_urn = member_id_link['data-semaphore-content-urn']
                member_id = member_urn.split(':')[-1]
            else:
                member_id = ""
        except Exception as e:
            print("An error occurred while extracting ID of the member: ", e)
            member_id = ""
        return member_id
    
    def extract_page_lang(self, soup):
        try:
            page_lang_link=soup.find('html')
            if page_lang_link:
                page_lang = page_lang_link.get('lang', '')
            else:
                page_lang = ""
        except Exception as e:
            print("An error occurred while extracting page language: ", e)
            page_lang = ""
        return{
            "Language of the page is: ": page_lang
        }

    def parse_html_content(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        retrieval_time = datetime.now()
        member_id = self.extract_member_id(soup)
        member_category = ""
        if member_id.isdigit():
            member_category = "public_member_id"
        elif member_id.startswith("ADo"):
            member_category = "public_linkedin_member_id"
        else:
            member_category = ""
        post_data = PostData(
            author_first_name=self.extract_author_name(soup)["First name of the author is: "],
            author_last_name=self.extract_author_name(soup)["Last name of the author is: "],
            author_title=self.extract_author_title(soup)["The title of the author is: "],
            post_content=self.extract_post_content(soup)["Content of the post: "],
            like_count=self.extract_like_count(soup)["Number of likes: "],
            comment_count=self.extract_comment_count(soup)["Number of comments: "],
            publish_date=self.extract_publish_date(soup)["The date of publishing is: "],
            member_id=member_id,
            page_lang=self.extract_page_lang(soup)["Language of the page is: "]
        )
        return post_data, retrieval_time, member_category
    
def main():
    linkedin_post_path = "linkedin_post.html"
    config_path = "config.json"

    parser = htmlParser(config_path)

    with open(linkedin_post_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    post_data, retrieval_time, member_category = parser.parse_html_content(html_content)

    for field_name in PostData.__dataclass_fields__:
        value = getattr(post_data, field_name)
        print(f"{field_name}: {value}")

    result = post_data.__dict__
    result["retrieval_time"] = retrieval_time.isoformat()
    result["member_category"] = member_category

    with open("post_data.json", "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)
    
if __name__ == "__main__":
    main()