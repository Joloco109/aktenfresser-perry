from playground import run_scrape
import schedule
import time

if __name__ == "__main__":

    schedule.every().day.at("12:00").do(run_scrape)
    run_scrape()
    while True:
        schedule.run_pending()
        time.sleep(60)
