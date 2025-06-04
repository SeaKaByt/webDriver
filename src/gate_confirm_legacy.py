def confirm_pickup(self) -> None:
    try:
        if not self.properties.visible(self.gt["search_tractor"], timeout=1):
            self.module_view(self.module)

        df, p = next(self.get_gate_pickup_data())

        for tractor, group in df.groupby("tractor"):
            self.actions.click(self.gt["gate_transaction_refresh_btn"])
            self.actions.click(self.gt["search_tractor"])
            send_keys_wlog(tractor)
            send_keys_wlog("%s")

            if self.properties.enabled(self.gt["confirm_btn"]):
                send_keys_wlog("%4")
            else:
                raise RuntimeError("Confirm button not enabled")

            twin_ind = group["twin_ind"].iloc[0]
            if twin_ind == "T":
                if wait_for_window("Confirm"):
                    self.actions.click(self.gt["confirm_yes_btn"])
                else:
                    raise RuntimeError("Confirm window not found")

                for _, row in group.iterrows():
                    if wait_for_window("Exit Gate Inspection"):
                        self.actions.click(self.gt["exit_gate_inspection_size"])
                        send_keys_wlog(row["size"])
                        send_keys_wlog(self.type)
                        self.actions.click(self.gt["inspection_seal"])
                        send_keys_wlog(self.seal_ind)
                        if row["status"] == "IF":
                            send_keys_wlog("F")
                        elif row["status"] == "EM":
                            send_keys_wlog("E")
                        send_keys_wlog(self.oog_ind)
                        send_keys_wlog("{ENTER}")

                for idx, row in group.iterrows():
                    if wait_for_window("Gate Confirm Information"):
                        self.actions.click(self.gt["gate_confirm_manual_confirm_btn"])
                    else:
                        raise RuntimeError("Gate Confirm Information window not found")

                    if idx == group.index[0] and wait_for_window("Gate Confirm"):
                        send_keys_wlog("{ENTER}")
                    elif idx == group.index[0]:
                        raise RuntimeError("Gate Confirm window not found")

            elif twin_ind == "S":
                if wait_for_window("Confirm"):
                    self.actions.click(self.gt["confirm_yes_btn"])
                else:
                    raise RuntimeError("Confirmation window not found")

                if wait_for_window("Exit Gate Inspection", timeout=1):
                    send_keys_wlog(group["size"].iloc[0])
                    send_keys_wlog(self.type)
                    self.actions.click(self.gt["inspection_seal"])
                    send_keys_wlog(self.seal_ind)
                    if group["status"].iloc[0] == "IF":
                        send_keys_wlog("F")
                    elif group["status"].iloc[0] == "EM":
                        send_keys_wlog("E")
                    send_keys_wlog(self.oog_ind)
                    send_keys_wlog("{ENTER}")

                if wait_for_window("Gate Confirm Information"):
                    self.actions.click(self.gt["gate_confirm_manual_confirm_btn"])
                else:
                    raise RuntimeError("Gate Confirm Information window not found")

                if wait_for_window("Gate Confirm"):
                    send_keys_wlog("{ENTER}")
                else:
                    raise RuntimeError("Gate Confirm window not found")

    except Exception as e:
        raise RuntimeError(f"Confirm pickup failed: {e}")


def confirm_ground(self) -> None:
    try:
        if not self.properties.visible(self.gt["search_tractor"], timeout=1):
            self.module_view(self.module)

        df, p = next(self.get_gate_ground_data())

        for idx, row in df.iterrows():
            self.actions.click(self.gt["gate_transaction_refresh_btn"])
            if idx % 2 == 0:
                self.actions.click(self.gt["search_tractor"])
                send_keys_wlog(row["tractor"])
                send_keys_wlog("%s")
            send_keys_wlog("%4")

            if wait_for_window("Gate Confirm Information", timeout=2):
                self.actions.click(self.gt["gate_confirm_manual_confirm_btn"])
            else:
                raise RuntimeError("Gate Confirm Information window not found")

            if wait_for_window("Gate Confirm", timeout=5):
                send_keys_wlog("{ENTER}")
            else:
                raise RuntimeError("Gate Confirm window not found")

    except Exception as e:
        raise RuntimeError(f"Confirm ground failed: {e}")