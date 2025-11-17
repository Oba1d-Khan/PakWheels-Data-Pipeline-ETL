import requests
from bs4 import BeautifulSoup
import csv  
import sys  
from utils.paths import get_data_path

out_csv = get_data_path('pakwheels_raw_data_.csv')

def scrape_and_save(num_pages=10, output_csv=out_csv):

    all_car_data = []

    # Use the 'num_pages' argument (add 1 because range stops early)
    for page_num in range(1, num_pages + 1):
        
        url_to_scrape = f"https://www.pakwheels.com/used-cars/search/-/?page={page_num}"
        
        print(f"--- Scraping Page {page_num} ---")
        print(url_to_scrape)
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url_to_scrape, headers=headers)
            response.raise_for_status() 

            soup = BeautifulSoup(response.text, 'lxml')
            
            listings_on_page = soup.find_all('div', class_='ad-container')
            
            if not listings_on_page:
                print("No listings found on this page. Stopping.")
                break

            for item in listings_on_page:
                
                car_info = {}

                try:
                    car_info['name'] = item.find('h3').text.strip()
                    car_info['price'] = item.find('div', class_='price-details').text.strip()
                    relative_url = item.find('a', class_='ad-detail-path')['href']
                    car_info['url'] = "https://www.pakwheels.com" + relative_url
                    car_info['location'] = item.find('ul', class_='search-vehicle-info').find('li').text.strip()
                except Exception as e:
                    continue 
                
                # handle properties that can be None
                car_info['year'] = None
                car_info['mileage'] = None
                car_info['fuel_type'] = None
                car_info['engine_cc'] = None
                car_info['transmission'] = None

                try:
                    specs_list_items = item.find('ul', class_='search-vehicle-info-2').find_all('li')
                    
                    if len(specs_list_items) > 0:
                        car_info['year'] = specs_list_items[0].text.strip()
                    if len(specs_list_items) > 1:
                        car_info['mileage'] = specs_list_items[1].text.strip()
                    if len(specs_list_items) > 2:
                        car_info['fuel_type'] = specs_list_items[2].text.strip()
                    if len(specs_list_items) > 3:
                        car_info['engine_cc'] = specs_list_items[3].text.strip()
                    if len(specs_list_items) > 4:
                        car_info['transmission'] = specs_list_items[4].text.strip()
                
                except AttributeError:
                    pass
                
                all_car_data.append(car_info)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {url_to_scrape}: {e}")
            continue

    print("\n✅ Scraping Complete!")
    print(f"Found a total of {len(all_car_data)} car listings.")

    print("\n--- First 10 Listings Found ---")
    for car in all_car_data[:10]:
        print(car)

    csv_filename = output_csv 

    if not all_car_data:
        print("No data found to save.")
        return # Exit the function

    try:
        print(f"\nWriting {len(all_car_data)} items to {csv_filename}...")
        
        # CSV header/column names
        all_headers = ['name', 'price', 'url', 'location', 'year', 'mileage', 'fuel_type', 'engine_cc', 'transmission']
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
            
            # extrasaction='ignore' ignores unknown fields/keys
            writer = csv.DictWriter(file, fieldnames=all_headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_car_data)
            
        print(f"✅ Successfully saved data to {csv_filename}")
    
    except PermissionError:
        print(f"\n❌ PERMISSION ERROR: Could not write to {csv_filename}.")
        print("   Please make sure the file is not open in Excel.")
        sys.exit() # Exit the script
    except Exception as e:
        print(f"\n❌ Error saving to CSV: {e}")
        sys.exit() # Exit the script


if __name__ == '__main__':
    print("\n--- Running web_scraper.py ... ---")
    scrape_and_save(num_pages=10, output_csv='PakWheels-Data-Pipeline/data/pakwheels_raw_data_.csv')