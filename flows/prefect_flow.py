from prefect import flow, task
from src.scraper import CarScraper
from scripts.analysis import analyze_data


@task
def scrape_task():
    scraper = CarScraper()
    df = scraper.scrape()
    scraper.save_data(df)
    return df


@task
def analysis_task(df):
    analyze_data(df)


@flow(name="Car Price Monitoring")
def main_flow():
    df = scrape_task()
    analysis_task(df)


if __name__ == "__main__":
    main_flow()
