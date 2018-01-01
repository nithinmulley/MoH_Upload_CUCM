#!/usr/bin/env python3
# -> Use this script to upload .wav files on your CUCM Cluster.
# -> MoH Files cannot contain spaces in the file names.
# -> Use the template YaML file to provide CUCM Cluster details.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common import exceptions as selenium_exceptions
from ntpath import basename
from multiprocessing.pool import ThreadPool
import itertools
import time
import sys
import yaml


# This function uploads the .wav file to all MoH servers defined in the pub_sub_ip_list
def uploadmoh(server_ip, moh_file_path, source_num, moh_file):
    global pub_updated
    global updated_servers
    global current_file
    driver = webdriver.Chrome(executable_path=settings['CHROME_DRIVER_PATH'])
    # driver.set_window_size(800, 600)
    driver.get(f"https://{server_ip}/ccmadmin/mohAudioFileUpload.do?type=mohAudioManagement")
    driver.find_element_by_name("j_username").send_keys(settings['app_user'])
    driver.find_element_by_name("j_password").send_keys(settings['app_pswd'])
    driver.find_element_by_name("j_password").send_keys(Keys.RETURN)
    time.sleep(2)
    driver.find_element_by_name("file").send_keys(moh_file_path)
    driver.find_element_by_name("Upload File").click()
    time.sleep(2)
    updated_servers.append(1)
    print(f"-> {len(updated_servers)} - Upload successful on {server_ip}")
    if server_ip == settings['pub_ip']:
        sleep_cnt = 0
        while len(updated_servers) < len(pub_sub_ip_list):
            time.sleep(2)
            sleep_cnt += 1
            if sleep_cnt > 20:
                print('''File not uploaded on all servers. Script timed out. Cannot proceed further.
                    Check the faulty server in the pub_sub_ip_list''')
                sys.exit()
        driver.get(f"https://{server_ip}/ccmadmin/mohServerFindList.do")
        driver.find_element_by_name("findButton").click()
        driver.find_element_by_name("masterCheckBox").click()
        driver.find_element_by_name("Reset Selected").click()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        driver.find_element_by_name("Reset").click()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.get(f"https://{settings['pub_ip']}/ccmadmin/mohAudioFindList.do")
        driver.find_element_by_name("findButton").click()
        driver.find_element_by_partial_link_text(str(source_num)).click()  # MOH SOURCE NUMBER
        web_elem = Select(driver.find_element_by_name("sourcefile"))
        current_file = web_elem.first_selected_option.text
        web_elem.select_by_visible_text(moh_file)
        driver.find_element_by_name("Save").click()
        pub_updated = 1
        print('\n-> New MoH Source file applied')
        print(f'\n-> Proceeding to delete file {current_file} on all MoH Servers')
        time.sleep(2)
    else:
        pass
    while not pub_updated:
        time.sleep(2)
    if settings['DELETE_OLD_SOURCE'] == 1 and current_file != moh_file:
        driver.get("https://{}/ccmadmin/mohAudioManagementFindList.do".format(server_ip))
        ref_xpath = "//input[@value='" + current_file + "']"
        try:
            web_elem = driver.find_element_by_xpath(ref_xpath)
            ref1 = (web_elem.get_attribute('name'))
            ref2 = ref1.split(".")[:-2][0]
            ref3 = ref2 + '.chked'
            driver.find_element_by_name(ref3).click()
            driver.find_element_by_name("Delete Selected").click()
            driver.switch_to.alert().accept()
            print(f"-> Delete successful on {server_ip}")
        except selenium_exceptions.NoSuchElementException as e:
            print(f"-> Unable to delete old MoH Source file on {server_ip}")
            print(e)
        time.sleep(1)
    driver.close()
    return


# Main function
def main():
    moh_file_path = input('Enter full path to the MoH File (Filename cannot contain spaces): ')
    # Check if .wav file
    if basename(moh_file_path).endswith('.wav') and not ' ' in basename(moh_file_path):
        moh_file = basename(moh_file_path).split('.')[0]
    else:
        print("Check Filename or File path,"
              "doesn't seem to be a .wav file or has space in the file name")
        sys.exit()
    print("*"*5 + ' Source Index ' + "*"*5)
    # Source numbers as per your CUCM Cluster MoH Sources
    print(settings['source_index'])
    print('\n-> Enter the MoH source number to which you want to apply the file'
          f'"{moh_file}"')
    source_num = int(input('-> Source Number: '))
    # Parallel Upload
    start_time = time.time()
    pool = ThreadPool(len(pub_sub_ip_list))
    results = pool.starmap(uploadmoh, 
                           zip(pub_sub_ip_list,
                            itertools.repeat(moh_file_path),
                            itertools.repeat(source_num),
                            itertools.repeat(moh_file)))
    pool.close()
    pool.join()
    end_time = time.time()
    print("Total time=", end_time - start_time)


if __name__ =='__main__':
    if len(sys.argv)<2:
        print (f'Usage: {sys.argv[0]} template.yaml')
        sys.exit()
    else:
        with open(sys.argv[1]) as f:
            settings = yaml.safe_load(f)
    pub_sub_ip_list = settings['pub_ip'] + settings['sub_ip_list']
    #Global Variables, these are accessed across parallel threads
    pub_updated = 0
    updated_servers = []
    current_file = ''
    main()
