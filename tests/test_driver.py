# import allure
# import pytest
#
# from core.base_driver import BaseDriver
# from helper.win_utils import focus_window
# from src.pages.inventory_operation.container_details import ContainerDetails
# from src.pages.inventory_operation.hold_release import HoldRelease
#
# @pytest.mark.core
# @allure.title("Driver Initialization Test")
# def test_driver_initialization():
#     """Test to ensure the BaseDriver initializes correctly."""
#     with BaseDriver() as d:
#         c = ContainerDetails()
#         h = HoldRelease()
#
#         focus_window("nGen")
#
#         c.click()
#         h.click()