from .container_details import ContainerDetails
from .discharge_container import DischargeContainer

if __name__ == '__main__':
    cd = ContainerDetails()
    dc = DischargeContainer()

    cd.create_cntr()
    dc.create_cntr()
    # python -m test_ui.flow.run
    # python -m test_ui.flow.discharge_container
    # python -m test_ui.flow.container_details
    # python -m test_ui.flow.discharge_container --debug
    # python -m test_ui.flow.container_details --debug