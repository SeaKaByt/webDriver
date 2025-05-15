from driver.base_driver import BaseDriver
from helper.logger import logger

def main():
    try:
        driver = BaseDriver()

        logger.info("Testing file reading in BaseDriver...")
        logger.info(f"YAML file path:\n {driver.config}")
        logger.info(f"JSON file path:\n {driver.config_j}")
        logger.info(f"Excel file path:\n {driver.gate_pickup_df}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()